import os
import ffmpeg_downloader as ffdl
from TTS.api import TTS
from pydub import AudioSegment

# Vincula o FFmpeg instalado localmente direto no pydub
AudioSegment.converter = ffdl.ffmpeg_path

PASTA_PROJETO = r"C:\XTTS"
CAMINHO_ROTEIRO = os.path.join(PASTA_PROJETO, "roteiro.txt")
CAMINHO_REF = os.path.join(PASTA_PROJETO, "referencia.wav")
CAMINHO_SAIDA = os.path.join(PASTA_PROJETO, "audio_final_completo.mp3")

print("Carregando o modelo XTTS v2 local... Por favor, aguarde.")
tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", gpu=False)

# Carrega o roteiro, limpa o bug do ponto final e divide por parágrafos
with open(CAMINHO_ROTEIRO, "r", encoding="utf-8") as f:
    paragrafos = []
    for linha in f.readlines():
        linha_limpa = linha.strip()
        if linha_limpa:
            # Substitui pontos finais por exclamações para manter a pausa sem falar a palavra "ponto"
            # Remove aspas para evitar que o modelo tente verbalizá-las
            linha_tratada = linha_limpa.replace(".", "!").replace('"', '').replace('“', '').replace('”', '')
            paragrafos.append(linha_tratada)

print(f"Roteiro carregado e tratado contra o bug do ponto! Total de {len(paragrafos)} blocos de texto para processar.")

audio_completo = AudioSegment.empty()
pasta_temp = os.path.join(PASTA_PROJETO, "temp")
os.makedirs(pasta_temp, exist_ok=True)

# Processa cada parágrafo separadamente
for i, trecho in enumerate(paragrafos):
    print(f"[{i+1}/{len(paragrafos)}] Processando: {trecho[:30]}...")
    
    arquivo_temp = os.path.join(pasta_temp, f"parte_{i}.wav")
    
    # Gera o áudio do pedaço atual
    tts.tts_to_file(
        text=trecho,
        speaker_wav=CAMINHO_REF,
        language="pt",
        file_path=arquivo_temp
    )
    
    # Adiciona ao arquivo final com uma pequena pausa de 0.5 segundos entre parágrafos
    segmento = AudioSegment.from_wav(arquivo_temp)
    audio_completo += segmento + AudioSegment.silent(duration=500)
    
    # Remove o arquivo temporário para não entulhar o HD
    os.remove(arquivo_temp)

# Salva o arquivo consolidado de longa duração direto em MP3
audio_completo.export(CAMINHO_SAIDA, format="mp3", bitrate="192k")
os.rmdir(pasta_temp)

print(f"\n🎉 SUCESSO! Seu áudio longo foi consolidado em MP3 em:\n{CAMINHO_SAIDA}")
