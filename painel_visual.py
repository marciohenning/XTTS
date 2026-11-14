import os
import subprocess
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox

PASTA_PROJETO = r"C:\XTTS"
SCRIPT_GERADOR = os.path.join(PASTA_PROJETO, "gerar_audio_longo.py")
ARQUIVO_ROTEIRO = os.path.join(PASTA_PROJETO, "roteiro.txt")
ARQUIVO_HISTORICO = os.path.join(PASTA_PROJETO, "historico_producao.txt")
PYTHON_VENV = os.path.join(PASTA_PROJETO, "venv", "Scripts", "python.exe")

class AplicativoXTTS:
    def __init__(self, root):
        self.root = root
        self.root.title("Estúdio de Voz Local - XTTS v2")
        self.root.geometry("720x520")
        self.root.configure(bg="#1e1e1e")

        # Título
        titulo = tk.Label(root, text="🎙️ Gerador de Áudios Longos (XTTS v2)", font=("Segoe UI", 16, "bold"), bg="#1e1e1e", fg="#ffffff")
        titulo.pack(pady=(15, 5))

        subtitulo = tk.Label(root, text="Pasta de Trabalho: C:\\XTTS", font=("Segoe UI", 9), bg="#1e1e1e", fg="#aaaaaa")
        subtitulo.pack(pady=(0, 15))

        # Frame dos Botões
        frame_botoes = tk.Frame(root, bg="#1e1e1e")
        frame_botoes.pack(pady=5)

        btn_estilo = {"font": ("Segoe UI", 10, "bold"), "width": 18, "pady": 8, "bd": 0, "cursor": "hand2"}

        self.btn_roteiro = tk.Button(frame_botoes, text="📝 1. Editar Roteiro", bg="#3a3d41", fg="white", command=self.abrir_roteiro, **btn_estilo)
        self.btn_roteiro.grid(row=0, column=0, padx=6)

        self.btn_gerar = tk.Button(frame_botoes, text="▶️ 2. GERAR ÁUDIO", bg="#28a745", fg="white", command=self.iniciar_geracao, **btn_estilo)
        self.btn_gerar.grid(row=0, column=1, padx=6)

        self.btn_pasta = tk.Button(frame_botoes, text="📂 Abrir Pasta", bg="#007acc", fg="white", command=self.abrir_pasta, **btn_estilo)
        self.btn_pasta.grid(row=0, column=2, padx=6)

        self.btn_hist = tk.Button(frame_botoes, text="📊 Ver Histórico", bg="#6c757d", fg="white", command=self.abrir_historico, **btn_estilo)
        self.btn_hist.grid(row=0, column=3, padx=6)

        # Área de Log / Terminal Visual
        lbl_console = tk.Label(root, text="Progresso e Diagnóstico em Tempo Real:", font=("Segoe UI", 9, "bold"), bg="#1e1e1e", fg="#cccccc", anchor="w")
        lbl_console.pack(fill="x", padx=20, pady=(15, 2))

        self.console = scrolledtext.ScrolledText(root, font=("Consolas", 9), bg="#121212", fg="#00ff66", insertbackground="white", state="disabled")
        self.console.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def escrever_console(self, texto):
        self.console.configure(state="normal")
        self.console.insert(tk.END, texto)
        self.console.see(tk.END)
        self.console.configure(state="disabled")

    def abrir_roteiro(self):
        if not os.path.exists(ARQUIVO_ROTEIRO):
            with open(ARQUIVO_ROTEIRO, "w", encoding="utf-8") as f:
                f.write("")
        os.startfile(ARQUIVO_ROTEIRO)

    def abrir_pasta(self):
        os.startfile(PASTA_PROJETO)

    def abrir_historico(self):
        if os.path.exists(ARQUIVO_HISTORICO):
            os.startfile(ARQUIVO_HISTORICO)
        else:
            messagebox.showinfo("Histórico", "Nenhum histórico gerado ainda. Gere seu primeiro áudio!")

    def iniciar_geracao(self):
        self.btn_gerar.configure(state="disabled", text="⏳ Processando...", bg="#d39e00")
        self.console.configure(state="normal")
        self.console.delete(1.0, tk.END)
        self.console.configure(state="disabled")
        
        thread = threading.Thread(target=self.executar_script, daemon=True)
        thread.start()

    def executar_script(self):
        try:
            # Força saída sem buffer (-u) para exibir cada linha imediatamente na tela
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"
            
            processo = subprocess.Popen(
                [PYTHON_VENV, "-u", SCRIPT_GERADOR],
                cwd=PASTA_PROJETO,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=env,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            for linha in processo.stdout:
                self.root.after(0, self.escrever_console, linha)

            processo.wait()
            self.root.after(0, self.finalizar_geracao, processo.returncode)
        except Exception as e:
            self.root.after(0, self.escrever_console, f"\n❌ Erro crítico: {e}\n")
            self.root.after(0, self.finalizar_geracao, 1)

    def finalizar_geracao(self, codigo_saida):
        self.btn_gerar.configure(state="normal", text="▶️ 2. GERAR ÁUDIO", bg="#28a745")
        if codigo_saida == 0:
            messagebox.showinfo("Concluído!", "🎉 Seu áudio MP3 foi gerado com sucesso na pasta C:\\XTTS!")

if __name__ == "__main__":
    root = tk.Tk()
    app = AplicativoXTTS(root)
    root.mainloop()
