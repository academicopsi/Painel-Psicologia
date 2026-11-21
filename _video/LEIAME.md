# Vídeo de divulgação da V3

Pasta de trabalho do vídeo de divulgação (não é publicada no site: o GitHub Pages ignora pastas que começam com `_`).

## O que tem aqui
- `gravar.py`: abre a V3 num navegador de teste com uma conta fictícia ("Ana Clara", apoiadora), preenche dados de estudo de demonstração e grava a tela do site rodando (Page.startScreencast), com marcas de tempo por trecho.
- `editar.py`: monta o vídeo vertical 1080×1920 a 30 fps: abertura com a frase de efeito, números do site contando, capítulos 01 a 06 (área, apoiador, Psiu, notificações, simulados, 1º período) com barra de progresso, celular com zoom de câmera e legendas animadas, encerramento.
- `musica.py`: compõe a trilha (100 bpm, A–E–F#m–D, subida antes da frase principal e impacto em cada capítulo).
- `mock_firebase.py`: troca o Firebase por uma versão falsa para gravar sem conta real.
- `narracao.txt`: roteiro da narração com o segundo em que cada bloco começa.
- `montar.sh`: roda tudo em sequência e gera `/tmp/vid/video_mudo.mp4` e `/tmp/vid/musica.wav`.
- `referencia-sem-narracao.mp4`: a versão aprovada até agora (música, sem narração).

## Próximo passo: narração masculina e natural
Pedido do Thiago: narração masculina e natural. A voz do Piper (Edresson) foi reprovada por soar robótica.
Plano: `pip install edge-tts` e gerar cada bloco de `narracao.txt` com a voz `pt-BR-AntonioNeural` (precisa de acesso à internet com "Todos os domínios").
Depois: colocar cada bloco no segundo indicado (adelay), juntar, abaixar a música quando a voz entra (sidechaincompress), normalizar em -15 LUFS e juntar ao vídeo com `-c:v copy`.
Se um bloco passar do tempo da cena, aumentar a velocidade da fala (`--rate=+8%`) antes de mexer nas cenas.

## Combinados
- Textos com "para", nunca "pra".
- Conta fictícia no vídeo (não mostrar nome nem e-mail do Thiago).
- Números de conteúdo reais (688 questões, 506 termos, 54 exercícios, 23 resumos, 12 disciplinas); os da área do apoiador são de demonstração.
- Endereço no final: academicopsi.github.io/Painel-Psicologia (a V3 vira o site oficial em 26/11).
