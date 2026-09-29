# 🎬 YouTube Chapter Splitter

Uma aplicação desktop moderna e intuitiva desenvolvida em Python para automatizar o download e o fatiamento de vídeos do YouTube em capítulos independentes, suportando tanto capítulos nativos do YouTube quanto minutagens inseridas manualmente pelo usuário.

---

## ✨ Funcionalidades

- 🔗 **Análise Automática de URL**: Valida a URL e consulta os metadados do vídeo para detectar capítulos nativos automaticamente.
- ⏱️ **Minutagem Customizada**: Permite colar ou editar a minutagem dos capítulos no formato `MM:SS - Nome` ou `HH:MM:SS - Nome`.
- 🎧 **Modo Apenas Áudio (MP3)**: Extrai diretamente as faixas de áudio dos capítulos em formato MP3 de alta qualidade.
- 🎬 **Modo Vídeo (MP4 / MKV)**: Escolha entre resoluções (Melhor Disponível, 1080p, 720p, 480p) e formatos de saída.
- ⚡ **Fatiamento Ultra-rápido**: Utiliza o motor do FFmpeg com cópia de stream (`-c copy`), fatiando os capítulos sem perda de qualidade e sem consumo excessivo de CPU.
- 🎨 **Interface Moderna**: Desenvolvida com CustomTkinter em modo escuro (Dark Theme), responsiva e amigável.
- 📦 **Executável Único Portable**: Compilado via PyInstaller em um único arquivo `.exe` sem necessidade de instalações adicionais no Windows.

---

## 🛠️ Tecnologias e Dependências Utilizadas

Este projeto foi construído utilizando as seguintes ferramentas e motores de mídia:

* **[CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)** - Interface gráfica moderna para Python baseada em Tkinter.
* **[yt-dlp](https://github.com/yt-dlp/yt-dlp)** - O motor principal para download de vídeos e extração de metadados/capítulos do YouTube.
* **[FFmpeg](https://www.ffmpeg.org/)** - Ferramenta líder para processamento, fatiamento e conversão multimídia de alta performance.
* **[PyInstaller](https://pyinstaller.org/)** - Empacotador para transformar a aplicação Python em um arquivo executável nativo do Windows.

---

## 📁 Estrutura do Projeto

```text
app-yt-dlp-chapter/
├── bin/                           # Executáveis locais de apoio (yt-dlp.exe, ffmpeg.exe)
├── src/
│   ├── __init__.py
│   ├── core.py                    # Lógica de download, análise de URL e corte via FFmpeg
│   └── gui.py                     # Interface gráfica do usuário (CustomTkinter)
├── main.py                        # Ponto de entrada da aplicação
├── requisitos.txt                 # Lista de dependências Python
├── YouTube_Chapter_Splitter.spec  # Arquivo de configuração de build do PyInstaller
├── prd-manual.md                  # PRD e Manual Técnico do produto
└── README.md                      # Documentação do repositório
```

---

## 🚀 Como Executar o Projeto

### Pré-requisitos
- **Python 3.10+** instalado em seu sistema.

### 1. Clonar o repositório
```bash
git clone https://github.com/seu-usuario/app-yt-dlp-chapter.git
cd app-yt-dlp-chapter
```

### 2. Instalar as dependências
```bash
pip install -r requisitos.txt
```

### 3. Executar a aplicação
```bash
python main.py
```

### 4. Gerar o Executável (.exe)
Para empacotar a aplicação em um arquivo `.exe` único pronto para distribuição:
```bash
pyinstaller --noconfirm YouTube_Chapter_Splitter.spec
```
O executável compilado estará disponível na pasta `dist/YouTube_Chapter_Splitter.exe`.

---

## 📄 Licença e Agradecimentos

Este projeto utiliza e referencia com orgulho os seguintes projetos de código aberto:
- **[yt-dlp](https://github.com/yt-dlp/yt-dlp)** (Licença Unlicense / Public Domain)
- **[FFmpeg](https://www.ffmpeg.org/)** (Licença LGPL/GPL)

---

<p align="center">
  <b>Desenvolvido com ❤ por Rogério Matsui Guenta e Inteligência Artificial</b>
</p>
