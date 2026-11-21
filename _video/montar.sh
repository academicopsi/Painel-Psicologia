#!/bin/bash
# Monta o vídeo de divulgação da V3 do zero. Uso: bash _video/montar.sh
set -e
REPO="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p /tmp/vid/ed && cp "$REPO"/_video/*.py /tmp/vid/
(setsid nohup python3 -m http.server 8765 --directory "$REPO" >/tmp/vid/srv.log 2>&1 &); sleep 1
python3 /tmp/vid/gravar.py                                    # 1. grava o site rodando (screencast)
cd /tmp/vid
python3 editar.py hook home numeros c1 area & python3 editar.py c2 apoio c3 psiu & python3 editar.py c4 mural c5 notif & python3 editar.py c6 sim c7 p1 fim & wait   # 2. edita as cenas
python3 musica.py                                             # 3. compõe a trilha
cd /tmp/vid/ed && printf "file '%s.mp4'\n" hook home numeros c1 area c2 apoio c3 psiu c4 mural c5 notif c6 sim c7 p1 fim > lista.txt
ffmpeg -y -loglevel error -f concat -safe 0 -i lista.txt -c copy /tmp/vid/video_mudo.mp4
echo "Vídeo sem som em /tmp/vid/video_mudo.mp4 e música em /tmp/vid/musica.wav. Falta a narração (ver LEIAME.md)."
