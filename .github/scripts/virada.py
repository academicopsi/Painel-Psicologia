# Virada: a V3 vira o site oficial (endereço sem /v3).
# Roda sozinho pelo workflow "Mural" a partir de 26/11/2026 10:00 (Brasília) e só faz algo uma vez.
# Uso manual: python3 .github/scripts/virada.py [--agora]
import os, re, shutil, sys, datetime

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
QUANDO = datetime.datetime(2026, 11, 26, 13, 0, tzinfo=datetime.timezone.utc)  # 10:00 em Brasília
MARCA = '<!-- virada: v3 virou o site oficial -->'

def ler(p): return open(os.path.join(RAIZ, p), encoding='utf-8').read()
def gravar(p, s):
    p = os.path.join(RAIZ, p); os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w', encoding='utf-8').write(s)
def trocar(s, a, b, arq, obrig=True):
    if a not in s:
        if obrig: sys.exit(f'virada: não achei em {arq}: {a[:60]}')
        return s
    return s.replace(a, b)

def main():
    agora = datetime.datetime.now(datetime.timezone.utc)
    if '--agora' not in sys.argv and agora < QUANDO:
        print('virada: ainda não é hora'); return False
    v3 = ler('v3/index.html')
    if MARCA in v3 or 'V3 (teste)' not in v3:
        print('virada: já feita'); return False

    # 1) a página da V3 vai para a raiz, com os caminhos ajustados
    s = v3
    for pasta in ('icons', 'divulgacao', 'arquivos'):
        s = s.replace(f'../{pasta}/', f'{pasta}/')
    s = trocar(s, '<title>V3 (teste) · ', '<title>', 'index.html')
    s = trocar(s, '<meta name="robots" content="noindex, nofollow">', '', 'index.html')
    if re.search(r'["\'(]\.\./', s): sys.exit('virada: sobrou caminho ../ na página')
    gravar('index.html', s)

    # 2) conteúdo que a página baixa sob demanda
    orig = os.path.join(RAIZ, 'v3', 'conteudo')
    for nome in os.listdir(orig):
        os.makedirs(os.path.join(RAIZ, 'conteudo'), exist_ok=True)
        shutil.copy2(os.path.join(orig, nome), os.path.join(RAIZ, 'conteudo', nome))

    # 3) /v3 passa a só redirecionar para o endereço oficial (links antigos continuam funcionando)
    gravar('v3/index.html', f'''<!DOCTYPE html>
<html lang="pt-BR"><head>{MARCA}
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex, nofollow">
<title>Arquivo Vivo</title>
<script>location.replace('../' + location.search + location.hash);</script>
<meta http-equiv="refresh" content="0; url=../">
</head><body style="font-family:sans-serif;padding:24px">
<p>O Arquivo Vivo mudou de endereço. <a href="../">Abrir o site</a></p>
</body></html>
''')

    # 4) avisos por notificação apontam para o endereço oficial
    n = ler('.github/scripts/notificar.mjs')
    n = trocar(n, "process.env.SITE_ARQUIVO || 'v3/index.html'", "process.env.SITE_ARQUIVO || 'index.html'", 'notificar.mjs')
    n = trocar(n, "'https://academicopsi.github.io/Painel-Psicologia/v3/'", "'https://academicopsi.github.io/Painel-Psicologia/'", 'notificar.mjs')
    gravar('.github/scripts/notificar.mjs', n)

    # 5) página de apresentação manda para o endereço oficial
    d = ler('divulgacao/index.html')
    d = trocar(d, 'const V3_ATE_A_VIRADA = true;', 'const V3_ATE_A_VIRADA = false;', 'divulgacao')
    d = d.replace('href="../v3/#', 'href="../#')
    gravar('divulgacao/index.html', d)

    # 6) service worker: deixa de guardar a /v3 e renova a cópia offline
    w = ler('firebase-messaging-sw.js')
    w = trocar(w, "const CACHE = 'av-offline-v1';", "const CACHE = 'av-offline-v2';", 'sw')
    w = trocar(w, "['', 'v3/', 'icons/icon-192.png', 'icons/icon-180.png', 'manifest.webmanifest', 'v3/manifest.webmanifest']",
                  "['', 'icons/icon-192.png', 'icons/icon-180.png', 'manifest.webmanifest']", 'sw')
    w = trocar(w, " || await c.match(new Request(u.origin + BASE + 'v3/'))", "", 'sw')
    gravar('firebase-messaging-sw.js', w)

    print('virada: feita'); return True

if __name__ == '__main__':
    feita = main()
    if os.environ.get('GITHUB_OUTPUT'):
        open(os.environ['GITHUB_OUTPUT'], 'a').write(f"feita={'1' if feita else '0'}\n")
