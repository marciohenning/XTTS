# ==========================================================
# XTTS STUDIO v1.0
# Interface gráfica para geração de áudio com XTTS
# Autor: Márcio + Copilot
# ==========================================================

import os
import threading
import subprocess
from tkinter import *
from tkinter import ttk, filedialog, messagebox
from datetime import datetime

# ==========================================================
# CONFIGURAÇÃO
# ==========================================================

PASTA_PROJETO = r"C:\XTTS"

ARQUIVO_GERADOR = os.path.join(
    PASTA_PROJETO,
    "gerar_audio_longo.py"
)

ARQUIVO_ROTEIRO = os.path.join(
    PASTA_PROJETO,
    "roteiro.txt"
)

ARQUIVO_SAIDA = os.path.join(
    PASTA_PROJETO,
    "audio_final_completo.mp3"
)

PASTA_VOZES = os.path.join(
    PASTA_PROJETO,
    "vozes"
)

# ==========================================================
# JANELA
# ==========================================================

root = Tk()

root.title(
    "XTTS Studio"
)

root.geometry(
    "850x650"
)

root.minsize(
    850,
    650
)

# ==========================================================
# VARIÁVEIS
# ==========================================================

arquivo_roteiro = StringVar()
arquivo_voz = StringVar()

arquivo_roteiro.set(
    ARQUIVO_ROTEIRO
)

# ==========================================================
# FUNÇÕES
# ==========================================================

def escrever_log(texto):

    log_text.config(
        state=NORMAL
    )

    log_text.insert(
        END,
        texto + "\n"
    )

    log_text.see(
        END
    )

    log_text.config(
        state=DISABLED
    )

    root.update_idletasks()


def selecionar_roteiro():

    caminho = filedialog.askopenfilename(
        title="Selecionar roteiro",
        filetypes=[
            ("Textos", "*.txt")
        ]
    )

    if caminho:

        arquivo_roteiro.set(
            caminho
        )

        escrever_log(
            f"📄 Roteiro selecionado: {caminho}"
        )


def carregar_vozes():

    combo_vozes["values"] = []

    if not os.path.exists(
        PASTA_VOZES
    ):
        os.makedirs(
            PASTA_VOZES,
            exist_ok=True
        )

    vozes = []

    for arquivo in os.listdir(
        PASTA_VOZES
    ):

        if arquivo.lower().endswith(
            ".wav"
        ):

            vozes.append(
                arquivo
            )

    combo_vozes["values"] = vozes

    if vozes:

        combo_vozes.current(
            0
        )

        arquivo_voz.set(
            vozes[0]
        )


def selecionar_voz(event=None):

    voz = combo_vozes.get()

    arquivo_voz.set(
        voz
    )


def copiar_arquivos():

    if not arquivo_roteiro.get():

        raise Exception(
            "Nenhum roteiro selecionado."
        )

    roteiro_origem = arquivo_roteiro.get()

    roteiro_destino = os.path.join(
        PASTA_PROJETO,
        "roteiro.txt"
    )

    if roteiro_origem != roteiro_destino:

        with open(
            roteiro_origem,
            "r",
            encoding="utf-8"
        ) as origem:

            conteudo = origem.read()

        with open(
            roteiro_destino,
            "w",
            encoding="utf-8"
        ) as destino:

            destino.write(
                conteudo
            )

    if arquivo_voz.get():

        voz_selecionada = os.path.join(
            PASTA_VOZES,
            arquivo_voz.get()
        )

        referencia = os.path.join(
            PASTA_PROJETO,
            "referencia.wav"
        )

        with open(
            voz_selecionada,
            "rb"
        ) as origem:

            dados = origem.read()

        with open(
            referencia,
            "wb"
        ) as destino:

            destino.write(
                dados
            )


def gerar_audio():

    try:

        progress["value"] = 0
        lbl_status.config(
            text="Preparando..."
        )

        escrever_log(
            "🚀 Iniciando geração..."
        )

        copiar_arquivos()

        comando = [
            "python",
            ARQUIVO_GERADOR
        ]

        processo = subprocess.Popen(
            comando,
            cwd=PASTA_PROJETO,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="ignore"
        )

        progresso_fake = 0

        while True:

            linha = processo.stdout.readline()

            if not linha and processo.poll() is not None:
                break

            if linha:

                escrever_log(
                    linha.strip()
                )

                progresso_fake += 1

                if progresso_fake < 95:

                    progress["value"] = progresso_fake

                lbl_status.config(
                    text="Gerando..."
                )

        codigo = processo.wait()

        progress["value"] = 100

        if codigo == 0:

            escrever_log(
                "✅ Processo concluído."
            )

            lbl_status.config(
                text="Concluído"
            )

            if os.path.exists(
                ARQUIVO_SAIDA
            ):

                tamanho = round(
                    os.path.getsize(
                        ARQUIVO_SAIDA
                    ) /
                    (1024 * 1024),
                    2
                )

                escrever_log(
                    f"🎵 MP3 gerado: {tamanho} MB"
                )

        else:

            lbl_status.config(
                text="Erro"
            )

            escrever_log(
                "❌ Falha na geração."
            )

    except Exception as e:

        messagebox.showerror(
            "Erro",
            str(e)
        )

        escrever_log(
            f"ERRO: {e}"
        )


def iniciar_thread():

    t = threading.Thread(
        target=gerar_audio
    )

    t.daemon = True

    t.start()


def abrir_pasta():

    os.startfile(
        PASTA_PROJETO
    )

# ==========================================================
# CABEÇALHO
# ==========================================================

titulo = Label(
    root,
    text="XTTS Studio",
    font=("Segoe UI", 20, "bold")
)

titulo.pack(
    pady=10
)

# ==========================================================
# ROTEIRO
# ==========================================================

frame1 = LabelFrame(
    root,
    text="Roteiro"
)

frame1.pack(
    fill=X,
    padx=10,
    pady=5
)

Entry(
    frame1,
    textvariable=arquivo_roteiro
).pack(
    side=LEFT,
    fill=X,
    expand=True,
    padx=5,
    pady=5
)

Button(
    frame1,
    text="Selecionar",
    command=selecionar_roteiro
).pack(
    side=RIGHT,
    padx=5
)

# ==========================================================
# VOZES
# ==========================================================

frame2 = LabelFrame(
    root,
    text="Voz"
)

frame2.pack(
    fill=X,
    padx=10,
    pady=5
)

combo_vozes = ttk.Combobox(
    frame2,
    width=50
)

combo_vozes.pack(
    side=LEFT,
    padx=5,
    pady=5
)

combo_vozes.bind(
    "<<ComboboxSelected>>",
    selecionar_voz
)

Button(
    frame2,
    text="Atualizar",
    command=carregar_vozes
).pack(
    side=LEFT,
    padx=5
)

# ==========================================================
# PROGRESSO
# ==========================================================

frame3 = LabelFrame(
    root,
    text="Progresso"
)

frame3.pack(
    fill=X,
    padx=10,
    pady=5
)

progress = ttk.Progressbar(
    frame3,
    length=800,
    mode="determinate"
)

progress.pack(
    fill=X,
    padx=10,
    pady=10
)

lbl_status = Label(
    frame3,
    text="Aguardando"
)

lbl_status.pack()

# ==========================================================
# BOTÕES
# ==========================================================

frame4 = Frame(
    root
)

frame4.pack(
    pady=10
)

Button(
    frame4,
    text="🎙️ GERAR ÁUDIO",
    font=("Segoe UI", 11, "bold"),
    command=iniciar_thread,
    bg="#58aa58"
).pack(
    side=LEFT,
    padx=10
)

Button(
    frame4,
    text="📂 Abrir Pasta",
    command=abrir_pasta
).pack(
    side=LEFT,
    padx=10
)

# ==========================================================
# LOG
# ==========================================================

frame5 = LabelFrame(
    root,
    text="Log"
)

frame5.pack(
    fill=BOTH,
    expand=True,
    padx=10,
    pady=10
)

log_text = Text(
    frame5,
    height=20
)

log_text.pack(
    fill=BOTH,
    expand=True
)

log_text.config(
    state=DISABLED
)

# ==========================================================
# INICIALIZAÇÃO
# ==========================================================

escrever_log(
    f"XTTS Studio iniciado em {datetime.now()}"
)

carregar_vozes()

root.mainloop()
