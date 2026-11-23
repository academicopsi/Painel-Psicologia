# Parte reservada da página de Experimental (gerador do trabalho ABNT): o código vai cifrado dentro da página
# e só abre com a sequência secreta (5 toques em "Arquivo Vivo · prévia" e depois 8 pronomes no teclado).
# Ler:    SEQ=xxxxxxxx python3 _privado/reservado.py ler > /tmp/codigo.js
# Gravar: SEQ=xxxxxxxx python3 _privado/reservado.py gravar /tmp/codigo.js
# SEQ = índices dos pronomes (0 Eu, 1 Tu, 2 Ele/Ela, 3 Nós, 4 Vós, 5 Eles/Elas). O código aberto nunca vai para o repositório.
import base64, os, sys, json, re
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
PAG = os.path.join(os.path.dirname(__file__), '..', 'p-4dc069c07026', 'index.html')
seq = os.environ['SEQ'].encode(); s = open(PAG, encoding='utf-8').read()
chave = lambda sal, it: PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=sal, iterations=it).derive(seq)
if sys.argv[1] == 'ler':
    P = json.loads(re.search(r"const P = (\{.*?\}), LS = 'av-priv-seq'", s, re.S).group(1))
    sys.stdout.write(AESGCM(chave(base64.b64decode(P['s']), P['i'])).decrypt(base64.b64decode(P['n']), base64.b64decode(P['c']), None).decode())
else:
    cod = open(sys.argv[2], encoding='utf-8').read(); sal, n, it = os.urandom(16), os.urandom(12), 310000
    pac = json.dumps({'s': base64.b64encode(sal).decode(), 'n': base64.b64encode(n).decode(), 'i': it, 'c': base64.b64encode(AESGCM(chave(sal, it)).encrypt(n, cod.encode(), None)).decode()})
    s = re.sub(r"const P = \{.*?\}, LS = 'av-priv-seq'", lambda m: 'const P = ' + pac + ", LS = 'av-priv-seq'", s, flags=re.S)
    open(PAG, 'w', encoding='utf-8').write(s)
