import os
import queue
import threading
import customtkinter as ctk
from tkinter import messagebox, filedialog
from src.core import VideoSplitterCore

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class AppInterface(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.core = VideoSplitterCore()

        self.title("YouTube Chapter Splitter")
        self.geometry("900x720")
        self.minsize(800, 650)

        self.fila_progresso = queue.Queue()

        self._build_ui()
        self._verificar_fila_progresso()

    def _build_ui(self):
        # Grid layout da janela principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # ------------------- 1. BARRA SUPERIOR ESCURA (HEADER) -------------------
        self.frame_top = ctk.CTkFrame(self, fg_color="#1a1a1a", corner_radius=0, height=80)
        self.frame_top.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        self.frame_top.grid_columnconfigure(1, weight=1)

        self.lbl_url = ctk.CTkLabel(
            self.frame_top,
            text="URL do Vídeo:",
            font=("Segoe UI", 13, "bold"),
            text_color="#ffffff"
        )
        self.lbl_url.grid(row=0, column=0, padx=(20, 10), pady=20, sticky="w")

        self.txt_url = ctk.CTkEntry(
            self.frame_top,
            placeholder_text="https://www.youtube.com/watch?v=...",
            font=("Segoe UI", 12),
            height=36
        )
        self.txt_url.grid(row=0, column=1, padx=(0, 10), pady=20, sticky="ew")

        self.btn_analisar = ctk.CTkButton(
            self.frame_top,
            text="Analisar",
            font=("Segoe UI", 12, "bold"),
            fg_color="#1f538d",
            hover_color="#163c66",
            height=36,
            width=110,
            command=self.analisar_video
        )
        self.btn_analisar.grid(row=0, column=2, padx=(0, 20), pady=20, sticky="e")

        # ------------------- 2. OPÇÕES DE CONFIGURAÇÃO DE MÍDIA -------------------
        self.frame_opcoes = ctk.CTkFrame(self, fg_color="#242424", corner_radius=8)
        self.frame_opcoes.grid(row=1, column=0, sticky="ew", padx=20, pady=(15, 10))
        self.frame_opcoes.grid_columnconfigure(3, weight=1)

        self.lbl_opcoes_titulo = ctk.CTkLabel(
            self.frame_opcoes,
            text="Opções de Saída:",
            font=("Segoe UI", 12, "bold")
        )
        self.lbl_opcoes_titulo.grid(row=0, column=0, padx=15, pady=12, sticky="w")

        self.chk_audio = ctk.CTkCheckBox(
            self.frame_opcoes,
            text="Apenas Áudio (MP3)",
            font=("Segoe UI", 12),
            command=self.alternar_modo_audio
        )
        self.chk_audio.grid(row=0, column=1, padx=15, pady=12, sticky="w")

        self.lbl_qualidade = ctk.CTkLabel(
            self.frame_opcoes,
            text="Resolução:",
            font=("Segoe UI", 12)
        )
        self.lbl_qualidade.grid(row=0, column=2, padx=(20, 5), pady=12, sticky="w")

        self.opt_qualidade = ctk.CTkOptionMenu(
            self.frame_opcoes,
            values=["Melhor Disponível", "1080p", "720p", "480p"],
            width=150
        )
        self.opt_qualidade.grid(row=0, column=3, padx=(0, 15), pady=12, sticky="w")

        self.lbl_formato = ctk.CTkLabel(
            self.frame_opcoes,
            text="Formato:",
            font=("Segoe UI", 12)
        )
        self.lbl_formato.grid(row=0, column=4, padx=(10, 5), pady=12, sticky="w")

        self.opt_formato = ctk.CTkOptionMenu(
            self.frame_opcoes,
            values=["MP4", "MKV"],
            width=90
        )
        self.opt_formato.grid(row=0, column=5, padx=(0, 15), pady=12, sticky="w")

        self.lbl_codec = ctk.CTkLabel(
            self.frame_opcoes,
            text="Codec Video:",
            font=("Segoe UI", 12)
        )
        self.lbl_codec.grid(row=0, column=6, padx=(10, 5), pady=12, sticky="w")

        self.opt_codec = ctk.CTkOptionMenu(
            self.frame_opcoes,
            values=["H.264 (Android)", "Original (Sem re-encode)"],
            width=170
        )
        self.opt_codec.grid(row=0, column=7, padx=(0, 15), pady=12, sticky="w")

        # ------------------- 3. ÁREA CENTRAL DE MINUTAGEM / CAPÍTULOS -------------------
        self.frame_central = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_central.grid(row=2, column=0, sticky="nsew", padx=20, pady=5)
        self.frame_central.grid_rowconfigure(1, weight=1)
        self.frame_central.grid_columnconfigure(0, weight=1)

        self.lbl_capitulos = ctk.CTkLabel(
            self.frame_central,
            text="Capítulos Detectados / Insira a Minutagem Manual:",
            font=("Segoe UI", 12, "bold")
        )
        self.lbl_capitulos.grid(row=0, column=0, sticky="w", pady=(5, 5))

        self.txt_capitulos = ctk.CTkTextbox(
            self.frame_central,
            font=("Consolas", 12),
            wrap="none"
        )
        self.txt_capitulos.grid(row=1, column=0, sticky="nsew")

        exemplo_padrao = (
            "00:00 - Introdução\n"
            "02:15 - Desenvolvimento\n"
            "08:45 - Conclusão"
        )
        self.txt_capitulos.insert("1.0", exemplo_padrao)

        # ------------------- 4. SELEÇÃO DE PASTA DE DESTINO -------------------
        self.frame_destino = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_destino.grid(row=3, column=0, sticky="ew", padx=20, pady=10)
        self.frame_destino.grid_columnconfigure(1, weight=1)

        self.lbl_destino = ctk.CTkLabel(
            self.frame_destino,
            text="Pasta de Destino:",
            font=("Segoe UI", 12, "bold")
        )
        self.lbl_destino.grid(row=0, column=0, padx=(0, 10), sticky="w")

        pasta_padrao = os.path.join(os.path.expanduser("~"), "Downloads", "Capitulos")
        self.txt_destino = ctk.CTkEntry(
            self.frame_destino,
            font=("Segoe UI", 11)
        )
        self.txt_destino.insert(0, pasta_padrao)
        self.txt_destino.grid(row=0, column=1, padx=(0, 10), sticky="ew")

        self.btn_destino = ctk.CTkButton(
            self.frame_destino,
            text="Selecionar Pasta",
            font=("Segoe UI", 11),
            width=130,
            command=self.selecionar_pasta
        )
        self.btn_destino.grid(row=0, column=2, sticky="e")

        # ------------------- 5. BARRA DE PROGRESSO E STATUS -------------------
        self.frame_status = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_status.grid(row=4, column=0, sticky="ew", padx=20, pady=5)
        self.frame_status.grid_columnconfigure(0, weight=1)

        self.lbl_status = ctk.CTkLabel(
            self.frame_status,
            text="Status: Aguardando comandos...",
            font=("Segoe UI", 11, "italic"),
            text_color="#aaaaaa"
        )
        self.lbl_status.grid(row=0, column=0, sticky="w")

        self.barra_progresso = ctk.CTkProgressBar(self.frame_status, height=12)
        self.barra_progresso.grid(row=1, column=0, sticky="ew", pady=5)
        self.barra_progresso.set(0)

        # ------------------- 6. BOTÃO INFERIOR DESTACADO -------------------
        self.btn_extrair = ctk.CTkButton(
            self,
            text="INICIAR EXTRAÇÃO",
            font=("Segoe UI", 14, "bold"),
            fg_color="#2b712b",
            hover_color="#1e4e1e",
            height=45,
            command=self.iniciar_thread_processamento
        )
        self.btn_extrair.grid(row=5, column=0, sticky="ew", padx=20, pady=(5, 20))

    def alternar_modo_audio(self):
        modo_audio = bool(self.chk_audio.get())
        state = "disabled" if modo_audio else "normal"
        self.opt_qualidade.configure(state=state)
        self.opt_formato.configure(state=state)
        self.opt_codec.configure(state=state)

    def selecionar_pasta(self):
        pasta = filedialog.askdirectory(title="Selecione a pasta para salvar os capítulos")
        if pasta:
            self.txt_destino.delete(0, "end")
            self.txt_destino.insert(0, pasta)

    def analisar_video(self):
        url = self.txt_url.get().strip()
        if not url:
            messagebox.showwarning("Aviso", "Por favor, insira a URL do vídeo do YouTube.")
            return

        self.btn_analisar.configure(state="disabled", text="Analisando...")
        self.lbl_status.configure(
            text="Status: Consultando capítulos e dados do vídeo no YouTube...",
            text_color="#1f538d"
        )

        def run_analise():
            try:
                info = self.core.analisar_url(url)
                self.fila_progresso.put(("analise_ok", info, ""))
            except Exception as e:
                self.fila_progresso.put(("analise_erro", None, str(e)))

        threading.Thread(target=run_analise, daemon=True).start()

    def iniciar_thread_processamento(self):
        url = self.txt_url.get().strip()
        if not url:
            messagebox.showwarning("Aviso", "Por favor, insira a URL do vídeo do YouTube.")
            return

        texto_capitulos = self.txt_capitulos.get("1.0", "end-1c").strip()
        
        # Validação antecipada da sintaxe dos capítulos
        try:
            self.core.validar_e_parsear_capitulos(texto_capitulos)
        except ValueError as ve:
            messagebox.showerror("Erro de Sintaxe", str(ve))
            return

        pasta_destino = self.txt_destino.get().strip()
        if not pasta_destino:
            pasta_destino = filedialog.askdirectory(title="Selecione onde salvar os capítulos")
            if not pasta_destino:
                return
            self.txt_destino.delete(0, "end")
            self.txt_destino.insert(0, pasta_destino)

        apenas_audio = bool(self.chk_audio.get())
        qualidade = self.opt_qualidade.get()
        formato = self.opt_formato.get()
        codec = self.opt_codec.get()

        self.btn_extrair.configure(state="disabled")
        self.btn_analisar.configure(state="disabled")
        self.barra_progresso.set(0)
        self.lbl_status.configure(text="Status: Preparando extração...", text_color="#1f538d")

        def cb_progresso(pct, msg):
            self.fila_progresso.put(("progresso", (pct, msg), ""))

        def cb_fim():
            self.fila_progresso.put(("sucesso", None, ""))

        def cb_erro(msg_erro):
            self.fila_progresso.put(("erro", None, msg_erro))

        self.core.iniciar_thread_processamento(
            texto_usuario=texto_capitulos,
            url_video=url,
            pasta_destino=pasta_destino,
            apenas_audio=apenas_audio,
            qualidade_video=qualidade,
            formato_video=formato,
            codec_video=codec,
            callback_progresso=cb_progresso,
            callback_fim=cb_fim,
            callback_erro=cb_erro
        )

    def _verificar_fila_progresso(self):
        try:
            while True:
                msg = self.fila_progresso.get_nowait()
                tipo, payload, texto = msg

                if tipo == "progresso":
                    pct, status_text = payload
                    self.barra_progresso.set(pct)
                    self.lbl_status.configure(text=f"Status: {status_text}", text_color="#1f538d")

                elif tipo == "sucesso":
                    self.barra_progresso.set(1.0)
                    self.lbl_status.configure(
                        text="Status: Processo concluído com sucesso!",
                        text_color="#2b712b"
                    )
                    messagebox.showinfo("Sucesso", "Todos os capítulos foram extraídos e salvos com sucesso!")
                    self.btn_extrair.configure(state="normal")
                    self.btn_analisar.configure(state="normal", text="Analisar")

                elif tipo == "erro":
                    self.lbl_status.configure(text=f"Status: Erro - {texto}", text_color="#d9534f")
                    messagebox.showerror("Erro na Extração", texto)
                    self.btn_extrair.configure(state="normal")
                    self.btn_analisar.configure(state="normal", text="Analisar")

                elif tipo == "analise_ok":
                    self.btn_analisar.configure(state="normal", text="Analisar")
                    info = payload
                    titulo = info['titulo']
                    nativos = info['capitulos_nativos']

                    if nativos:
                        self.lbl_status.configure(
                            text=f"Vídeo: {titulo} ({len(nativos)} capítulos nativos encontrados)",
                            text_color="#2b712b"
                        )
                        self.txt_capitulos.delete("1.0", "end")
                        self.txt_capitulos.insert("1.0", "\n".join(nativos))
                    else:
                        self.lbl_status.configure(
                            text=f"Vídeo: {titulo} (Sem capítulos automáticos)",
                            text_color="#e67e22"
                        )
                        exemplo = (
                            "Este vídeo não possui capítulos automáticos. Insira sua minutagem abaixo:\n\n"
                            "00:00 - Introdução\n"
                            "01:30 - Parte 1\n"
                            "05:00 - Conclusão"
                        )
                        self.txt_capitulos.delete("1.0", "end")
                        self.txt_capitulos.insert("1.0", exemplo)

                elif tipo == "analise_erro":
                    self.btn_analisar.configure(state="normal", text="Analisar")
                    self.lbl_status.configure(text=f"Status: Erro na análise", text_color="#d9534f")
                    messagebox.showerror("Erro de Análise", texto)

        except queue.Empty:
            pass

        self.after(100, self._verificar_fila_progresso)


if __name__ == "__main__":
    app = AppInterface()
    app.mainloop()
