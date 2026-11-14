import os
import glob
from TTS.api import TTS
from pydub import AudioSegment

PASTA_PROJETO = r"C:\XTTS"
PASTA_ROTEIROS = os.path.join(PASTA_PROJETO, "roteiros_fila")
CAMINHO_REF = os.path.join(PASTA_PROJETO, "referencia.wav")

# Cria a pasta de roteiros caso ela não exista
os.makedirs(PASTA_ROTEIROS, exist_ok=True)

# Busca todos os arquivos .txt dentro da pasta da fila
arquivos_txt = glob.glob(os.path.join(PASTA_ROTEIROS, "*.txt"))

if not arquivos_txt:
    print(f"Nenhum arquivo .txt encontrado em: {PASTA_ROTEIROS}")
    print("Coloque seus roteiros lá dentro e execute o script novamente!")
    exit()

print(f"--- FILA ENCONTRADA: {len(arquivos_txt)} projeto(s) para processar ---")
print("Carregando o modelo XTTS v2 local... Por favor, aguarde.")
tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", gpu=False)

for idx, caminho_txt in enumerate(arquivos_txt):
    nome_base = os.path.splitext(os.path.basename(caminho_txt))[0]
    caminho_saida_audio = os.path.join(PASTA_PROJETO, f"audio_{nome_base}.wav")
    
    print(f"\n=========================================")
    print(f"PROJETO [{idx+1}/{len(arquivos_txt)}]: Processando '{nome_base}'")
    print(f"=========================================")
    
    # Carrega o roteiro atual e divide por parágrafos
    with open(caminho_txt, "r", encoding="utf-8") as f:
        paragrafos = [p.strip() for p in f.readlines() if p.strip()]
        
    audio_completo = AudioSegment.empty()
    pasta_temp = os.path.join(PASTA_PROJETO, "temp_fila")
    os.makedirs(pasta_temp, exist_ok=True)
    
    # Processa os parágrafos do texto atual
    for i, trecho in enumerate(paragrafos):
        print(f"  -> Gerando bloco [{i+1}/{len(paragrafos)}]")
        arquivo_temp = os.path.join(pasta_temp, f"parte_{i}.wav")
        
        tts.tts_to_file(
            text=trecho,
            speaker_wav=CAMINHO_REF,
            language="pt",
            file_path=arquivo_temp
        )
        
        segmento = AudioSegment.from_wav(arquivo_temp)
        audio_completo += segmento + AudioSegment.silent(duration=500) # 0.5s de pausa natural
        os.remove(arquivo_temp)
        
    # Exporta o áudio final com o nome correspondente do texto
    audio_completo.export(caminho_saida_audio, format="wav")
    os.rmdir(pasta_temp)
    print(f"🎉 Concluído com sucesso! Áudio salvo como: audio_{nome_base}.wav")

print("\n🚀 PARABÉNS! Todos os áudios da sua fila foram gerados com sucesso!")
