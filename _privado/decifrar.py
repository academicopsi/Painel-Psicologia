# Recupera a página aberta a partir do arquivo cifrado, para editar. Uso:
# SENHA='...' python3 _privado/decifrar.py p-4dc069c07026/index.html > /tmp/experimental-aberto.html
# Depois de editar, cifre de novo com cifrar.py (o PowerPoint já vem embutido na página aberta, então não precisa passar de novo).
import base64, os, sys, json, re
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
s = open(sys.argv[1], encoding='utf-8').read()
P = json.loads(re.search(r'const P = (\{.*?\});', s).group(1))
k = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=base64.b64decode(P['s']), iterations=P['i']).derive(os.environ['SENHA'].encode())
sys.stdout.write(AESGCM(k).decrypt(base64.b64decode(P['n']), base64.b64decode(P['c']), None).decode('utf-8'))
