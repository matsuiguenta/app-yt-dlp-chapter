### Documento de Requisitos do Produto (PRD) & Manual Técnico

**Projeto:** YouTube Chapter Splitter App
**Versão:** 1.0
**Status:** Pronto para Desenvolvimento 

### 1. Visão Geral do Produto

O **YouTube Chapter Splitter** é uma ferramenta (Desktop ou Web) projetada para automatizar o download e o fatiamento de vídeos do YouTube com base em capítulos. Ele resolve o problema de usuários que precisam apenas de trechos específicos de vídeos longos (como podcasts, aulas ou álbuns musicais), permitindo escolher formatos, qualidades e oferecendo suporte a capítulos customizados caso o vídeo original não os possua. 

### Core Técnico

O motor do aplicativo será baseado no [yt-dlp](https://github.com/yt-dlp/yt-dlp) e no [FFmpeg](https://www.ffmpeg.org/), encapsulando a complexidade da linha de comando em uma interface gráfica simples e intuitiva (UI/UX). 

### Estrutura

app-yt-dlp-chapter/
│
├── bin/
│   ├── yt-dlp.exe      # Executável do yt-dlp
│   └── ffmpeg.exe      # Executável do FFmpeg
│
├── src/
│   ├── __init__.py
│   ├── gui.py          # Interface Visual (CustomTkinter)
│   └── core.py         # Lógica de download e corte (yt-dlp/FFmpeg)
│
├── main.py             # Arquivo principal que inicia o app
├── requisitos.txt      # Dependências (customtkinter, etc.)│
└── prd-manual.md		# PRD e Manual do Usuário - YouTube Chapter Splitter


### 2. Requisitos Funcionais (Escopo do Aplicativo)

### RF01: Entrada de URL e Análise

* O usuário deve inserir um link válido do YouTube.
* O sistema deve validar a URL e consultar a API do yt-dlp (--dump-json) para verificar se o vídeo possui capítulos nativos.

### RF02: Configuração de Mídia (Qualidade e Formato)

* **Modo Vídeo:** 

  * O usuário pode escolher entre resoluções: **Melhor Disponível, 1080p, 720p, 480p**.
  * Formatos de saída obrigatórios: **MP4** ou **MKV**.
* **Modo Apenas Áudio:** 

  * Caixa de seleção (Checkbox): *"Extrair apenas o áudio dos capítulos"*.
  * Ao marcar, oculta as opções de resolução de vídeo e força a saída em **MP3** (ou permite selecionar qualidade do áudio: 320kbps, 192kbps).

### RF03: Gerenciamento de Capítulos (Nativos vs. Manuais)

* **Cenário A (Capítulos Nativos Detectados):** O app exibe a lista de capítulos encontrados no vídeo com caixas de seleção ao lado de cada um (permitindo ao usuário baixar todos ou apenas capítulos específicos).
* **Cenário B (Sem Capítulos Nativos):** O app exibe uma área de texto vazia (Text Area) com a mensagem: *"Este vídeo não possui capítulos automáticos. Insira sua minutagem abaixo"*. 

  * O sistema deve aceitar o formato padrão: MM:SS - Nome do Capítulo ou HH:MM:SS - Nome do Capítulo.
  * **Regra de Validação:** O primeiro item inserido manualmente deve obrigatoriamente começar em 00:00 (ou 00:00:00).

### RF04: Processamento e Download

* O app deve criar uma pasta temporária para o download do vídeo completo.
* O app deve disparar os comandos de corte usando o FFmpeg de forma silenciosa em segundo plano.
* O app deve exibir uma **barra de progresso global** ou por capítulo para o usuário.
* Ao finalizar, deve limpar o arquivo temporário completo e deixar apenas os capítulos na pasta de destino escolhida pelo usuário.

### 3. Arquitetura de Comandos (O que o App executa por trás)

Para o desenvolvedor responsável pelo back-end do app, estas são as strings de comando que o código deve montar e disparar no sistema operacional: 

### Cenário 1: Vídeo com Capítulos Nativos do YouTube

O aplicativo montará a string dinamicamente com base nas escolhas da interface. 

* **Se o usuário escolheu VÍDEO (MP4) na melhor qualidade:** 

bash

yt-dlp --split-chapters -f "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]" -o "chapter:%(chapter_number)s - %(chapter)s.%(ext)s" "URL_DO_VIDEO"

Use o código com cuidado.
* **Se o usuário escolheu APENAS ÁUDIO (MP3):** 

bash

yt-dlp --split-chapters -x --audio-format mp3 --audio-quality 0 -o "chapter:%(chapter_number)s - %(chapter)s.%(ext)s" "URL_DO_VIDEO"

Use o código com cuidado.

### Cenário 2: Vídeo SEM Capítulos (Inserção Manual do Usuário)

Quando o usuário digita a minutagem manualmente na interface, o yt-dlp não consegue usar o --split-chapters diretamente de forma nativa. O aplicativo terá duas rotas de desenvolvimento possíveis: 

### Rota Recomendada para o Desenvolvedor (Injeção de Metadados via FFmpeg)

O aplicativo deve baixar o vídeo completo normalmente e, antes de cortar, rodar um comando FFmpeg para injetar os capítulos que o usuário digitou em um arquivo de texto de metadados, ou efetuar o corte direto loopando as linhas fornecidas pelo usuário: 

bash

# Exemplo de lógica de loop interna que o App fará via FFmpeg para cada linha inserida:
ffmpeg -ss [TEMPO_INICIO] -to [TEMPO_FIM] -i "video_completo.mp4" -c copy "Nome_do_Capitulo.mp4"

Use o código com cuidado.

### 4. Manual de UX/UI e Fluxo de Telas (Mockup Conceitual)

### Tela Inicial (Aguardando Link)

+-----------------------------------------------------------------------+

|                       YOUTUBE CHAPTER SPLITTER                        |
+-----------------------------------------------------------------------+

|  Insira a URL do vídeo do YouTube:                                    |
|  [ https://www.youtube.com/watch?v=XYZ123                       ] [OK] |
+-----------------------------------------------------------------------+

### Tela de Configuração (Após clicar em OK)

+-----------------------------------------------------------------------+

| Opções de Saída:                                                     |
| ( ) Vídeo  [ Resolução: 1080p v ] [ Formato: MP4 v ]                  |
| (X) Apenas Áudio (Converter capítulos para MP3)                       |
+-----------------------------------------------------------------------+

| Capítulos Detectados / Customizados:                                  |
| +-------------------------------------------------------------------+ |
| | [X] 00:00 - Introdução                                            | |
| | [X] 04:15 - Desenvolvimento do Código                             | |
| | [ ] 12:30 - Testes de Erros                                       | |
| | [X] 18:45 - Conclusão e Encerramento                              | |
| +-------------------------------------------------------------------+ |
|                                                                       |
| [ Selecionar Pasta de Destino ] -> C:\Usuário\Downloads\Capitulos     |
|                                                                       |
|                                                    [ INICIAR EXTRAÇÃO ]|
+-----------------------------------------------------------------------+

### Mensagem de Erro / Validação de Input Manual

Se o usuário tentar digitar capítulos manualmente e esquecer o formato ou a origem 00:00, a interface deve retornar o seguinte alerta: 

❌ **Erro de Sintaxe:** Certifique-se de que a primeira linha comece estritamente com 00:00 ou 00:00:00 e que haja um espaço ou hífen separando o tempo do nome do capítulo. 

### 5. Critérios de Aceite para Homologação (Testes de QA)

1. **Teste de Carga:** Baixar um vídeo de mais de 2 horas e verificar se o fatiamento não corrompe a sincronia de áudio e vídeo (problema comum de dessincronização do FFmpeg se não usar o comando -c copy ou reencodificação apropriada).
2. **Teste de Caractere Especial:** Verificar se capítulos com caracteres como /, \, *, ?, : no nome automático do YouTube não quebram o salvamento do arquivo no Windows (o sistema deve sanitizar os nomes dos arquivos substituindo caracteres proibidos por underscores _).
3. **Cancelamento:** Se o usuário clicar em "Cancelar" no meio do processo, o App deve encerrar imediatamente os processos órfãos do yt-dlp.exe e ffmpeg.exe no Gerenciador de Tarefas e apagar os arquivos temporários parciais.