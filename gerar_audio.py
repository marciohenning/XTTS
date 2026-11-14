import os
from TTS.api import TTS

# 1. Caminhos dos arquivos organizados na pasta
PASTA_PROJETO = r"C:\XTTS"
CAMINHO_ROTEIRO = os.path.join(PASTA_PROJETO, "roteiro.txt")
CAMINHO_REF = os.path.join(PASTA_PROJETO, "referencia.wav")
CAMINHO_SAIDA = os.path.join(PASTA_PROJETO, "audio_final_clonado.wav")

print("Carregando o modelo XTTS v2 local... Por favor, aguarde.")
# Inicializa o modelo usando o processador (CPU)
tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", gpu=False)

# 2. Ler o roteiro longo do arquivo .txt
if not os.path.exists(CAMINHO_ROTEIRO):
    print(f"Erro: Crie o arquivo 'roteiro.txt' em {PASTA_PROJETO} antes de rodar.")
    exit()

with open(CAMINHO_ROTEIRO, "r", encoding="utf-8") as f:
    texto_roteiro = f.read().strip()

print(f"Roteiro carregado com sucesso ({len(texto_roteiro)} caracteres).")
print("Iniciando a clonagem e geração do áudio longo... Isso pode demorar alguns minutos.")

# 3. Gera o áudio final clonando a voz do seu arquivo 'referencia.wav'
tts.tts_to_file(
    text=texto_roteiro,
    speaker_wav=CAMINHO_REF,
    language="pt",
    file_path=CAMINHO_SAIDA
)

print(f"\n🎉 SUCESSO! Seu áudio de longa duração foi gerado e salvo em:\n{CAMINHO_SAIDA}")
