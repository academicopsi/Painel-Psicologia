#!/bin/bash
# Monta o vídeo de divulgação da V3 do zero. Uso: bash _video/montar.sh
set -e
REPO="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p /tmp/vid/ed && cp "$REPO"/_video/*.py /tmp/vid/
(setsid nohup python3 -m http.server 8765 --directory "$REPO" >/tmp/vid/srv.log 2>&1 &); sleep 1
python3 /tmp/vid/gravar.py                                    # 1. grava o site rodando (screencast) e salva o PDF do simulado
python3 /tmp/vid/psiu.py && pdftoppm -r 110 -png /tmp/vid/simulado.pdf /tmp/vid/pdfh   # Psiu em PNG e páginas do PDF
cd /tmp/vid
python3 editar.py tempos
python3 editar.py hook home numeros c1 plano & python3 editar.py c2 pdf c3 apoio c4 & python3 editar.py psiu c5 mural & python3 editar.py c6 notif c7 sim c8 p1 fim & wait   # 2. edita as cenas
python3 musica.py                                             # 3. compõe a trilha
cd /tmp/vid/ed && printf "file '%s.mp4'\n" hook home numeros c1 plano c2 pdf c3 apoio c4 psiu c5 mural c6 notif c7 sim c8 p1 fim > lista.txt
ffmpeg -y -loglevel error -f concat -safe 0 -i lista.txt -c copy /tmp/vid/video_mudo.mp4
echo "Vídeo sem som em /tmp/vid/video_mudo.mp4 e música em /tmp/vid/musica.wav. Falta a narração (ver LEIAME.md)."
