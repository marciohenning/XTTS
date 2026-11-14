import os
import re
import time
from datetime import datetime
import torch
import ffmpeg_downloader as ffdl
from TTS.api import TTS
from pydub import AudioSegment
from pydub.silence import detect_leading_silence

# Vincula o FFmpeg instalado localmente direto no pydub
AudioSegment.converter = ffdl.ffmpeg_path

PASTA_PROJETO = r"C:\XTTS"
CAMINHO_ROTEIRO = os.path.join(PASTA_PROJETO, "roteiro.txt")
CAMINHO_REF = os.path.join(PASTA_PROJETO, "referencia.wav")
CAMINHO_SAIDA = os.path.join(PASTA_PROJETO, "audio_final_completo.mp3")
CAMINHO_HISTORICO = os.path.join(PASTA_PROJETO, "historico_producao.txt")

# 1. Prevenção: Verifica se os arquivos existem antes de carregar o modelo
if not os.path.exists(CAMINHO_ROTEIRO):
    print(f"❌ ERRO: O arquivo '{CAMINHO_ROTEIRO}' não foi encontrado!")
    exit()

if not os.path.exists(CAMINHO_REF):
    print(f"❌ ERRO: O áudio de referência '{CAMINHO_REF}' não foi encontrado!")
    exit()

# Prevenção: Faz backup automático se você esquecer de mover o áudio anterior
if os.path.exists(CAMINHO_SAIDA):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_backup = os.path.join(PASTA_PROJETO, f"backup_audio_{timestamp}.mp3")
    os.rename(CAMINHO_SAIDA, caminho_backup)
    print(f"⚠️ Áudio anterior salvo como backup: {os.path.basename(caminho_backup)}")

# Detecta automaticamente se há placa de vídeo NVIDIA para acelerar (sem alterar a voz)
usar_gpu = torch.cuda.is_available()
dispositivo_nome = torch.cuda.get_device_name(0) if usar_gpu else "Processador (CPU)"

print(f"Carregando o modelo XTTS v2 local em: {dispositivo_nome}...")
tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", gpu=usar_gpu)

# Remove os segundos mortos de silêncio que o modelo deixa nas pontas de cada bloco
def aparar_silencio(audio_seg, limite_db=-45.0):
    inicio_corte = detect_leading_silence(audio_seg, silence_threshold=limite_db)
    fim_corte = detect_leading_silence(audio_seg.reverse(), silence_threshold=limite_db)
    duracao = len(audio_seg)
    if inicio_corte + fim_corte >= duracao:
        return audio_seg
    return audio_seg[inicio_corte:duracao - fim_corte]

# Limpa símbolos que causam ruídos, mascara o ponto final e reforça verbos no futuro
def tratar_fonetica_e_pontuacao(texto):
    texto = texto.replace('\u200b', '').replace('\xa0', ' ')
    texto = re.sub(r'\.{2,}', ',', texto)
    texto = texto.replace('—', ',').replace('–', ',').replace(' - ', ', ')
    texto = re.sub(r'["“”\'()\[\]{}*#_]', '', texto)
    # Usa ponto e vírgula no meio e exclamação no fim para evitar o bug de ler "ponto" sem dramatizar demais
    texto = re.sub(r'\.(?=\s+\w)', ';', texto)
    texto = texto.replace(".", "!")
    # Reforça verbos oxítonos no futuro (apresentará, será, tornará, etc.)
    texto = re.sub(r'\b(\w+(?:rá|rão))\b(?![!?,;:])', r'\1,', texto)
    texto = re.sub(r'[,;]\s*[,;]', ',', texto)
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto

# Garante que nenhuma frase ultrapasse 195 caracteres (evita corte de palavras no limite de 203 do PT-BR)
def fatiar_frase_longa(frase, limite=195):
    if len(frase) <= limite:
        return [frase]
    
    pedacos = []
    parte_atual = ""
    sub_trechos = re.split(r'(?<=[,;:])\s+', frase)
    
    for sub in sub_trechos:
        while len(sub) > limite:
            corte = sub.rfind(' ', 0, limite)
            if corte == -1:
                corte = limite
            if parte_atual:
                pedacos.append(parte_atual)
                parte_atual = ""
            pedacos.append(sub[:corte].strip())
            sub = sub[corte:].strip()

        if len(parte_atual) + len(sub) + 1 <= limite:
            parte_atual = (parte_atual + " " + sub).strip()
        else:
            if parte_atual:
                pedacos.append(parte_atual)
            parte_atual = sub
            
    if parte_atual:
        pedacos.append(parte_atual)
    return pedacos

# 2. Leitura e tratamento do roteiro
with open(CAMINHO_ROTEIRO, "r", encoding="utf-8") as f:
    texto_bruto = f.read()

chars_brutos = len(texto_bruto.strip())
if chars_brutos == 0:
    print("❌ ERRO: O arquivo 'roteiro.txt' está vazio!")
    exit()

frases_seguras = []
for linha in texto_bruto.splitlines():
    limpa = linha.strip()
    if limpa:
        tratada = tratar_fonetica_e_pontuacao(limpa)
        if tratada:
            frases_seguras.extend(fatiar_frase_longa(tratada, limite=195))

# Agrupa frases muito curtas até ~195 caracteres para evitar fala picada ("soluços")
paragrafos = []
bloco_atual = ""

for linha in frases_seguras:
    if not bloco_atual:
        bloco_atual = linha
    elif len(bloco_atual) + len(linha) + 1 <= 195:
        bloco_atual += " " + linha
    else:
        paragrafos.append(bloco_atual)
        bloco_atual = linha

if bloco_atual:
    paragrafos.append(bloco_atual)

# 3. Diagnóstico e Prevenção de Erros antes de gerar
texto_completo = " ".join(paragrafos)
total_caracteres_tratados = len(texto_completo)
total_palavras = len(texto_completo.split())
media_palavras_bloco = round(total_palavras / len(paragrafos), 1)
maior_bloco_chars = max(len(p) for p in paragrafos)

segundos_estimados = int((total_palavras / 105) * 60)
est_min = segundos_estimados // 60
est_seg = segundos_estimados % 60

numeros_encontrados = set(re.findall(r'\b\d+\b', texto_completo))
romanos_encontrados = set(re.findall(r'\b(?=[MDCLXVI]+\b)M{0,4}(?:CM|CD|D?C{0,3})(?:XC|XL|L?X{0,3})(?:IX|IV|V?I{0,3})\b', texto_completo))
siglas_reais = {s for s in re.findall(r'\b[A-Z]{2,5}\b', texto_completo) if not re.search(r'[AEIOU]{2,}', s) and len(s) <= 4 and s not in {'UMA', 'DOS', 'DAS', 'COM', 'POR', 'QUE', 'NAO', 'SIM', 'MAS', 'ATO'}}

print("\n=======================================================")
print("📊 DIAGNÓSTICO DO ROTEIRO (APERFEIÇOADO + VELOCIDADE ORIGINAL)")
print(f"   - Hardware Ativo:          {dispositivo_nome}")
print(f"   - Caracteres Originais:    {chars_brutos} chars")
print(f"   - Caracteres Tratados:     {total_caracteres_tratados} chars (em {len(paragrafos)} blocos)")
print(f"   - Total de Palavras:       {total_palavras} palavras")
print(f"   - Média por Bloco:         {media_palavras_bloco} palavras")
print(f"   - Maior Bloco Gerado:      {maior_bloco_chars} chars (Limite seguro: 203)")
print(f"   - Duração Estimada:        ~{est_min}m {est_seg}s")

if numeros_encontrados:
    print(f"   ⚠️ ALERTA DE NÚMEROS:      Encontrados {list(numeros_encontrados)} (escreva por extenso).")
if romanos_encontrados:
    print(f"   ⚠️ ALERTA DE ROMANOS:      Encontrados {list(romanos_encontrados)} (troque por 'século vinte', etc.).")
if siglas_reais:
    print(f"   ⚠️ ALERTA DE SIGLAS:       Encontradas {list(siglas_reais)} (verifique a pronúncia).")
print("=======================================================\n")

# 4. Processamento na Velocidade Original
inicio_processamento = time.time()
audio_completo = AudioSegment.empty()
pasta_temp = os.path.join(PASTA_PROJETO, "temp")
os.makedirs(pasta_temp, exist_ok=True)

chars_processados_acumulado = 0

for i, trecho in enumerate(paragrafos):
    chars_trecho = len(trecho)
    chars_processados_acumulado += chars_trecho
    print(f"[{i+1}/{len(paragrafos)}] ({chars_trecho} chars | {chars_processados_acumulado}/{total_caracteres_tratados}) -> {trecho[:32]}...")
    
    arquivo_temp = os.path.join(pasta_temp, f"parte_{i}.wav")
    
    # Gera o áudio mantendo a velocidade original exata
    tts.tts_to_file(
        text=trecho,
        speaker_wav=CAMINHO_REF,
        language="pt",
        file_path=arquivo_temp
    )
    
    # Corta sobras vazias e adiciona uma pausa natural equilibrada (300ms)
    segmento_bruto = AudioSegment.from_wav(arquivo_temp)
    segmento_limpo = aparar_silencio(segmento_bruto)
    audio_completo += segmento_limpo + AudioSegment.silent(duration=300)
    
    os.remove(arquivo_temp)

# Salva o arquivo consolidado em MP3 e remove a pasta temporária
audio_completo.export(CAMINHO_SAIDA, format="mp3", bitrate="192k")
os.rmdir(pasta_temp)

# 5. Relatório Final e Registro no Histórico
fim_processamento = time.time()
tempo_gasto_seg = int(fim_processamento - inicio_processamento)
proc_min = tempo_gasto_seg // 60
proc_seg = tempo_gasto_seg % 60

duracao_audio_seg = len(audio_completo) / 1000.0
audio_min = int(duracao_audio_seg) // 60
audio_seg = int(duracao_audio_seg) % 60

wpm_real = round(total_palavras / (duracao_audio_seg / 60.0), 1) if duracao_audio_seg > 0 else 0
rtf = round(tempo_gasto_seg / duracao_audio_seg, 2) if duracao_audio_seg > 0 else 0
tamanho_mb = round(os.path.getsize(CAMINHO_SAIDA) / (1024 * 1024), 2)

if wpm_real < 90:
    status_ritmo = "Muito Lento (abaixo de 90 WPM)"
elif wpm_real > 150:
    status_ritmo = "Rápido (acima de 150 WPM)"
else:
    status_ritmo = "Ideal / Natural para Narração (entre 90 e 150 WPM)"

relatorio_final = f"""
=======================================================
🎉 RELATÓRIO FINAL DE PRODUÇÃO ({datetime.now().strftime('%d/%m/%Y %H:%M')})
   - Hardware Utilizado:    {dispositivo_nome}
   - Arquivo Salvo:         {CAMINHO_SAIDA} ({tamanho_mb} MB)
   - Duração Real do Áudio: {audio_min}m {audio_seg}s
   - Tempo de Geração (PC): {proc_min}m {proc_seg}s (Fator RTF: {rtf}x)
   - Caracteres Tratados:   {total_caracteres_tratados} chars (Original: {chars_brutos})
   - Palavras Geradas:      {total_palavras} palavras
   - Ritmo de Narração:     {wpm_real} palavras/min -> {status_ritmo}
=======================================================
"""

print(relatorio_final)

with open(CAMINHO_HISTORICO, "a", encoding="utf-8") as hist:
    hist.write(relatorio_final)
