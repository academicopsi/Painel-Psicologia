# Desenha o Psiu neutro (óculos e sorriso) em PNG transparente, a partir das funções de desenho do próprio site.
import subprocess
html=open('/home/claude/painel-psicologia/v3/index.html').read()
defs=[html[html.index('  const '+n+' = '):html.index('\n',html.index('  const '+n+' = '))] for n in ['CEREBRO','OCULOS','PUPILAS','BOCA']]
open('/tmp/vid/psiu_defs.js','w').write('\n'.join(defs)+"\nconsole.log(CEREBRO()+OCULOS()+PUPILAS()+BOCA('M50 72 Q60 80 70 72'));\n")
s=subprocess.run(['node','/tmp/vid/psiu_defs.js'],capture_output=True,text=True).stdout
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome'); pg=b.new_page(viewport={'width':600,'height':600}, device_scale_factor=2)
    pg.set_content('<html><body style="margin:0;background:transparent"><svg viewBox="0 0 120 120" style="width:600px;height:600px;display:block">'+s+'</svg></body></html>')
    pg.wait_for_timeout(300); pg.screenshot(path='/tmp/vid/psiu.png', omit_background=True); b.close()
from PIL import Image; im=Image.open('/tmp/vid/psiu.png'); im.crop(im.getbbox()).save('/tmp/vid/psiu.png')
