import os
import re
import sys
import json
import subprocess
import threading

def resolve_bin_path(binary_name):
    """
    Resolve o caminho dos executáveis (yt-dlp.exe e ffmpeg.exe)
    funcionando tanto em ambiente de desenvolvimento quanto empacotado via PyInstaller.
    """
    # Se estiver rodando através do PyInstaller (_MEIPASS)
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        meipass_bin = os.path.join(sys._MEIPASS, 'bin', binary_name)
        if os.path.exists(meipass_bin):
            return meipass_bin
        meipass_flat = os.path.join(sys._MEIPASS, binary_name)
        if os.path.exists(meipass_flat):
            return meipass_flat

    # Diretório raiz do projeto (um nível acima de src)
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    local_bin = os.path.join(root_dir, 'bin', binary_name)
    if os.path.exists(local_bin):
        return local_bin

    cwd_bin = os.path.join(os.getcwd(), 'bin', binary_name)
    if os.path.exists(cwd_bin):
        return cwd_bin

    return binary_name


class VideoSplitterCore:
    def __init__(self, bin_folder="bin"):
        self.ytdlp_path = resolve_bin_path("yt-dlp.exe")
        self.ffmpeg_path = resolve_bin_path("ffmpeg.exe")

    def converter_para_segundos(self, tempo_str):
        """Converte formatos MM:SS ou HH:MM:SS para o total em segundos."""
        partes = list(map(int, tempo_str.split(':')))
        if len(partes) == 2:  # MM:SS
            return partes[0] * 60 + partes[1]
        elif len(partes) == 3:  # HH:MM:SS
            return partes[0] * 3600 + partes[1] * 60 + partes[2]
        return 0

    def validar_e_parsear_capitulos(self, texto_usuario):
        """
        Valida a sintaxe do texto de minutagem digitado pelo usuário.
        Regra RF03: O primeiro capítulo DEVE obrigatoriamente começar em 00:00 ou 00:00:00.
        """
        linhas = [l.strip() for l in texto_usuario.split('\n') if l.strip()]
        if not linhas:
            raise ValueError("❌ Erro de Sintaxe: Insira ao menos um capítulo com minutagem.")

        primeira_linha = linhas[0]
        if not re.match(r'^00:00(:00)?\b', primeira_linha):
            raise ValueError(
                "Erro de Sintaxe: Certifique-se de que a primeira linha comece estritamente com 00:00 ou 00:00:00 e que haja um espaço ou hífen separando o tempo do nome do capítulo."
            )

        capitulos = []
        for i, linha in enumerate(linhas):
            match = re.match(r'^(\d{1,2}:\d{2}(?::\d{2})?)\s*[-–—.]?\s*(.*)', linha)
            if not match:
                raise ValueError(
                    f"Erro de Sintaxe na linha {i+1}: '{linha}'. Certifique-se do formato 'MM:SS - Nome do Capítulo'."
                )
            tempo_str, titulo = match.groups()
            titulo_limpo = titulo.strip() if titulo.strip() else f"Capitulo {i+1}"
            titulo_sanitizado = re.sub(r'[\\/*?:"<>|]', "_", titulo_limpo)
            segundos = self.converter_para_segundos(tempo_str)

            capitulos.append({
                "inicio_str": tempo_str,
                "segundos_inicio": segundos,
                "titulo": titulo_sanitizado
            })

        capitulos.sort(key=lambda x: x['segundos_inicio'])
        return capitulos

    def analisar_url(self, url_video):
        """
        Consulta a API do yt-dlp (--dump-json) para obter títulos e capítulos nativos se existirem.
        """
        if not url_video or not url_video.strip():
            raise ValueError("Por favor, informe uma URL válida do YouTube.")

        cmd = [self.ytdlp_path, "--dump-json", "--no-playlist", url_video.strip()]
        
        try:
            # Em Windows, ocultar janela do console ao rodar o comando subprocess
            creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            resultado = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                creationflags=creationflags,
                check=True
            )
            data = json.loads(resultado.stdout)
        except Exception as e:
            raise ValueError(f"Falha ao analisar a URL do vídeo: {str(e)}")

        titulo_video = data.get('title', 'Vídeo sem título')
        duracao = data.get('duration', 0)
        chapters = data.get('chapters')

        capitulos_formatados = []
        if chapters:
            for cap in chapters:
                start_sec = int(cap.get('start_time', 0))
                h = start_sec // 3600
                m = (start_sec % 3600) // 60
                s = start_sec % 60
                time_str = f"{h:02d}:{m:02d}:{s:02d}" if h > 0 else f"{m:02d}:{s:02d}"
                title_cap = cap.get('title', f"Capítulo {len(capitulos_formatados) + 1}")
                capitulos_formatados.append(f"{time_str} - {title_cap}")

        return {
            'titulo': titulo_video,
            'duracao': duracao,
            'capitulos_nativos': capitulos_formatados
        }

    def verificar_codec_h264(self, caminho_arquivo):
        """Verifica via FFmpeg se o arquivo já possui streams H.264 / AVC e AAC."""
        try:
            creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            proc = subprocess.run(
                [self.ffmpeg_path, "-i", caminho_arquivo],
                capture_output=True,
                text=True,
                creationflags=creationflags
            )
            stderr = proc.stderr.lower()
            contem_h264 = ("h264" in stderr or "avc1" in stderr or "avc " in stderr)
            return contem_h264
        except Exception:
            return False

    def processar_capitulos_manuais(
        self,
        texto_usuario,
        url_video,
        pasta_destino,
        apenas_audio=False,
        qualidade_video="Melhor Disponível",
        formato_video="MP4",
        codec_video="H.264 (Android)",
        progress_callback=None
    ):
        """
        Baixa o vídeo base e realiza a divisão em capítulos usando FFmpeg em background.
        """
        capitulos = self.validar_e_parsear_capitulos(texto_usuario)

        if not os.path.exists(pasta_destino):
            os.makedirs(pasta_destino, exist_ok=True)

        if progress_callback:
            progress_callback(0.10, "Iniciando download do vídeo base...")

        arquivo_temporario = os.path.join(pasta_destino, "_temp_full_video.mp4")

        # Define opções de download com base na escolha de qualidade/formato/codec
        forcar_h264 = (codec_video == "H.264 (Android)")

        if forcar_h264:
            if qualidade_video == "1080p":
                format_opt = "bv*[vcodec^=avc1][height<=1080]+ba[acodec^=mp4a]/bv*[height<=1080][ext=mp4]+ba[ext=m4a]/b[height<=1080][ext=mp4]/best"
            elif qualidade_video == "720p":
                format_opt = "bv*[vcodec^=avc1][height<=720]+ba[acodec^=mp4a]/bv*[height<=720][ext=mp4]+ba[ext=m4a]/b[height<=720][ext=mp4]/best"
            elif qualidade_video == "480p":
                format_opt = "bv*[vcodec^=avc1][height<=480]+ba[acodec^=mp4a]/bv*[height<=480][ext=mp4]+ba[ext=m4a]/b[height<=480][ext=mp4]/best"
            else:
                format_opt = "bv*[vcodec^=avc1]+ba[acodec^=mp4a]/bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/best"
        else:
            if qualidade_video == "1080p":
                format_opt = "bv*[height<=1080][ext=mp4]+ba[ext=m4a]/b[height<=1080][ext=mp4]/best"
            elif qualidade_video == "720p":
                format_opt = "bv*[height<=720][ext=mp4]+ba[ext=m4a]/b[height<=720][ext=mp4]/best"
            elif qualidade_video == "480p":
                format_opt = "bv*[height<=480][ext=mp4]+ba[ext=m4a]/b[height<=480][ext=mp4]/best"
            else:
                format_opt = "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/best"

        cmd_download = [
            self.ytdlp_path,
            "-f", format_opt,
            "-o", arquivo_temporario,
            "--no-playlist",
            url_video
        ]

        creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        proc_dl = subprocess.run(
            cmd_download,
            capture_output=True,
            text=True,
            creationflags=creationflags
        )

        if proc_dl.returncode != 0:
            if os.path.exists(arquivo_temporario):
                os.remove(arquivo_temporario)
            raise RuntimeError(f"Erro no download com yt-dlp: {proc_dl.stderr[:200]}")

        # Verifica se o vídeo baixado já é H.264
        ja_e_h264 = self.verificar_codec_h264(arquivo_temporario)

        if progress_callback:
            progress_callback(0.60, "Download concluído! Cortando capítulos...")

        total_capitulos = len(capitulos)

        for i, cap in enumerate(capitulos):
            inicio = cap["segundos_inicio"]
            titulo = cap["titulo"]
            num_capitulo = str(i + 1).zfill(2)

            if i < total_capitulos - 1:
                fim = capitulos[i + 1]["segundos_inicio"]
                duracao = fim - inicio
                parametro_tempo = ["-ss", str(inicio), "-t", str(duracao)]
            else:
                parametro_tempo = ["-ss", str(inicio)]

            ext = "mp3" if apenas_audio else formato_video.lower()
            nome_arquivo_final = f"{num_capitulo} - {titulo}.{ext}"
            caminho_saida = os.path.join(pasta_destino, nome_arquivo_final)

            if apenas_audio:
                cmd_corte = [
                    self.ffmpeg_path, "-y"
                ] + parametro_tempo + [
                    "-i", arquivo_temporario,
                    "-vn", "-acodec", "libmp3lame", "-aq", "2",
                    caminho_saida
                ]
            elif forcar_h264 and not ja_e_h264:
                # Caso a fonte original seja AV1/VP9 e o usuário pediu compatibilidade Android H.264
                cmd_corte = [
                    self.ffmpeg_path, "-y"
                ] + parametro_tempo + [
                    "-i", arquivo_temporario,
                    "-c:v", "libx264", "-preset", "fast", "-crf", "22",
                    "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k",
                    caminho_saida
                ]
            else:
                # Stream copy direto (rápido)
                cmd_corte = [
                    self.ffmpeg_path, "-y"
                ] + parametro_tempo + [
                    "-i", arquivo_temporario,
                    "-c", "copy",
                    caminho_saida
                ]

            proc_corte = subprocess.run(
                cmd_corte,
                capture_output=True,
                creationflags=creationflags
            )

            if proc_corte.returncode != 0:
                print(f"Aviso no corte do capítulo {num_capitulo}: {proc_corte.stderr}")

            pct = 0.60 + (0.38 * ((i + 1) / total_capitulos))
            if progress_callback:
                progress_callback(pct, f"Cortando capítulo {i+1} de {total_capitulos}...")

        # Limpeza do arquivo bruto temporário
        if os.path.exists(arquivo_temporario):
            try:
                os.remove(arquivo_temporario)
            except Exception:
                pass

        if progress_callback:
            progress_callback(1.0, "Processo concluído com sucesso!")

    def iniciar_thread_processamento(
        self,
        texto_usuario,
        url_video,
        pasta_destino,
        apenas_audio,
        qualidade_video,
        formato_video,
        codec_video,
        callback_progresso,
        callback_fim,
        callback_erro
    ):
        """Dispara o processamento em background."""
        def run():
            try:
                def on_progress(p, status):
                    callback_progresso(p, status)

                self.processar_capitulos_manuais(
                    texto_usuario=texto_usuario,
                    url_video=url_video,
                    pasta_destino=pasta_destino,
                    apenas_audio=apenas_audio,
                    qualidade_video=qualidade_video,
                    formato_video=formato_video,
                    codec_video=codec_video,
                    progress_callback=on_progress
                )
                callback_fim()
            except Exception as e:
                callback_erro(str(e))

        t = threading.Thread(target=run, daemon=True)
        t.start()
        return t
