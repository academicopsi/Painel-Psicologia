# Cifra a página privada de Experimental: o repositório só guarda o conteúdo cifrado (AES-GCM, chave PBKDF2-SHA256).
# Uso: SENHA='...' python3 _privado/cifrar.py <pagina-aberta.html> <slides.pptx> > p-4dc069c07026/index.html
# A página aberta nunca vai para o repositório (fica fora dele, com quem cuida do site).
import base64, os, sys, json
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
ITER = 310000
html = open(sys.argv[1], encoding='utf-8').read()
if len(sys.argv) > 2:  # o PowerPoint vai junto, dentro do conteúdo cifrado
    b = base64.b64encode(open(sys.argv[2], 'rb').read()).decode()
    html = html.replace("pptx: 'experimento-pronomes-40-slides.pptx'", "pptx: 'data:application/vnd.openxmlformats-officedocument.presentationml.presentation;base64," + b + "'")
    html = html.replace('${EXH.pptx}" download>', '${EXH.pptx}" download="experimento-pronomes-40-slides.pptx">')
senha = os.environ['SENHA'].encode()
sal, nonce = os.urandom(16), os.urandom(12)
chave = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=sal, iterations=ITER).derive(senha)
ct = AESGCM(chave).encrypt(nonce, html.encode('utf-8'), None)
pacote = json.dumps({'s': base64.b64encode(sal).decode(), 'n': base64.b64encode(nonce).decode(), 'i': ITER, 'c': base64.b64encode(ct).decode()})
sys.stdout.write(open(os.path.join(os.path.dirname(__file__), 'cofre.html'), encoding='utf-8').read().replace('__PACOTE__', pacote))
