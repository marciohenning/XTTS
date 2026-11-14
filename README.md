# 🎙️ Estúdio de Voz Local — XTTS v2 (Windows)

> **Viva Cristo Rei!**

Sistema completo de **Síntese de Voz (Text-to-Speech)** e **Clonagem de Voz** rodando 100% localmente no Windows, com interface gráfica própria, tratamento fonético automático para português e métricas detalhadas de produção — sem custos de API e sem limites de uso.

---

## ✨ Principais Recursos

* **Interface Gráfica Própria (`painel_visual.py`):** Controle tudo por botões clicáveis sem precisar digitar comandos no terminal.
* **Suporte a Áudios Longos (`gerar_audio_longo.py`):** Fatia textos extensos em blocos seguros (até 195 caracteres) para respeitar o limite do modelo em português, evitando cortes na fala.
* **Tratamento Fonético e de Pontuação:**
  * Elimina o bug do XTTS v2 de pronunciar a palavra *"ponto"* por extenso.
  * Reforça a tonicidade de verbos oxítonos no futuro (ex: *apresentará*, *será*) para manter o sentido correto.
  * Corta automaticamente os segundos de silêncio vazio nas pontas de cada bloco gerado.
* **Diagnóstico e Prevenção de Erros:** Verifica números e numerais romanos antes de iniciar, faz backup automático de áudios anteriores e registra o ritmo real em **Palavras por Minuto (WPM)** no arquivo `historico_producao.txt`.
* **Exportação Direta em MP3:** Consolida todos os blocos em um único arquivo `.mp3` de alta qualidade (192 kbps).

---

## 📂 Estrutura do Projeto (`C:\XTTS`)

* `gerar_audio_longo.py` — Motor principal de IA, tratamento fonético, corte de silêncio e métricas.
* `painel_visual.py` — Interface visual em Tkinter com console de progresso em tempo real.
* `Estudio_Voz_IA.bat` — Atalho executável para abrir a janela gráfica sem exibir o terminal preto.
* `gerar_fila.py` — Script auxiliar para processar múltiplos roteiros em lote.
* `Documentacao_Completa_Estudio_XTTS.pdf` — Manual técnico ilustrado com toda a arquitetura do sistema.

---

## 🛠️ Passo a Passo de Instalação (Windows)

### 1. Pré-requisitos
* **Python 3.11 (64-bits)** instalado no Windows.
* Pelo menos **10 GB livres** em disco (o modelo XTTS v2 ocupa ~1,88 GB).

### 2. Configuração do Ambiente Virtual
Abra o Prompt de Comando (CMD) e execute os comandos na ordem exata abaixo para alinhar as versões estáveis e evitar conflitos de DLL no Windows:

```cmd
mkdir C:\XTTS
cd C:\XTTS
python -m venv venv
venv\Scripts\activate

python -m pip install --upgrade pip setuptools wheel

pip install torch==2.4.1 torchaudio==2.4.1
pip install "transformers<4.45.0"
pip install coqui-tts==0.24.2
pip install "numpy<2.0,>=1.17"
pip install soundfile scipy six pydub ffmpeg-downloader

ffdl install
```

### 3. Preparando a Voz e o Roteiro
1. **Áudio de Referência (`referencia.wav`):** Coloque um áudio limpo (sem música de fundo) de 6 a 15 segundos da voz que deseja clonar dentro de `C:\XTTS` (formato WAV PCM 16-bit real).
2. **Roteiro (`roteiro.txt`):** Crie ou edite o arquivo `roteiro.txt` na mesma pasta. Escreva números e siglas por extenso (ex: *"mil novecentos e trinta e três"*, *"século vinte"*) para garantir a pronúncia perfeita.

---

## 🚀 Como Usar no Dia a Dia

1. Dê dois cliques no atalho **`Estudio_Voz_IA.bat`** (você pode copiá-lo para a sua Área de Trabalho).
2. Clique em **1. Editar Roteiro**, cole o texto desejado, salve e feche o Bloco de Notas.
3. Clique em **2. GERAR AUDIO** e acompanhe o diagnóstico e o progresso na tela.
4. Ao concluir, clique em **Abrir Pasta** e renomeie o arquivo **`audio_final_completo.mp3`** gerado.

---

## 🙏 Recomendação Especial

> *Se isso ajudou você de alguma maneira, reze uma Ave Maria agradecendo pelo Conhecimento e ajude pessoas que necessitam aprender essas tecnologias.*
>
> **Que Deus e Nossa Senhora o abençoe.**  
> **Viva Cristo Rei!**
