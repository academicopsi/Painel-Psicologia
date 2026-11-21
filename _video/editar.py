import json, os, subprocess, sys, math, bisect
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W,H,FPS=1080,1920,30
SERIF='/usr/share/fonts/truetype/google-fonts/Lora-Variable.ttf'; SERIF_I='/usr/share/fonts/truetype/google-fonts/Lora-Italic-Variable.ttf'
INTER_SB='/usr/share/fonts/opentype/inter/Inter-SemiBold.otf'; INTER_M='/usr/share/fonts/opentype/inter/Inter-Medium.otf'; INTER_B='/usr/share/fonts/opentype/inter/Inter-Bold.otf'
MINT=(169,211,200); OCRE=(214,158,82); CREME=(232,240,236)
def fnt(path,sz,w=None):
    f=ImageFont.truetype(path,sz)
    if w:
        try: f.set_variation_by_axes([w])
        except Exception: pass
    return f
def ease(k): k=max(0,min(1,k)); return 1-(1-k)**3
def ease_io(k): k=max(0,min(1,k)); return 3*k*k-2*k*k*k
# ---------- fundo ----------
def mkfundo():
    im=Image.new('RGB',(W,H)); d=ImageDraw.Draw(im)
    for y in range(H):
        t=y/H; d.line([(0,y),(W,y)],fill=tuple(int(a+(b-a)*t) for a,b in zip((0x23,0x62,0x5B),(0x0E,0x29,0x27))))
    g=Image.new('L',(W,H),0); ImageDraw.Draw(g).ellipse((W-560,-460,W+360,460),fill=60); g=g.filter(ImageFilter.GaussianBlur(170))
    im.paste((255,255,255),(0,0),g)
    for x in range(27,W,54):
        for y in range(27,H,54): d.ellipse((x,y,x+3,y+3),fill=(48,98,92))
    return im
FUNDO=mkfundo()
# ---------- gravação ----------
REC=json.load(open('/tmp/vid/rec.json')); FR=REC['frames']; FT=[t for _,t in FR]; T0=FT[0]
SEG={n:t-T0 for n,t in REC['segs']}
_cache={}
def tela(ts):
    i=max(0,bisect.bisect_right(FT,ts+T0)-1); f=FR[i][0]
    if f not in _cache:
        if len(_cache)>40: _cache.clear()
        _cache[f]=Image.open(f).convert('RGB')
    return _cache[f]
SCALE=0.84; SW,SH=int(780*SCALE),int(1560*SCALE)
MASK=Image.new('L',(SW,SH),0); ImageDraw.Draw(MASK).rounded_rectangle((0,0,SW,SH),radius=48,fill=255)
PW,PH=SW+32,SH+32
BEZ=Image.new('RGBA',(PW,PH),(0,0,0,0)); ImageDraw.Draw(BEZ).rounded_rectangle((0,0,PW-1,PH-1),radius=62,fill=(13,26,25,255),outline=(70,110,104,255),width=3)
SOMB=Image.new('L',(W,H),0)
def celular(base, shot, cx, cy, zoom, focy=None):
    # monta o celular e aplica zoom de câmera ao redor de (cx, focy)
    ph=BEZ.copy(); s=shot.resize((SW,SH),Image.BILINEAR); ph.paste(s,(16,16),MASK)
    pw,phh=int(PW*zoom),int(PH*zoom)
    ph=ph.resize((pw,phh),Image.BILINEAR) if zoom!=1 else ph
    fy = phh/2 if focy is None else (16+focy*SCALE)*zoom
    x=int(cx-pw/2); y=int(cy-fy)
    sh=Image.new('L',(pw+120,phh+120),0); ImageDraw.Draw(sh).rounded_rectangle((60,80,pw+60,phh+70),radius=int(62*zoom),fill=130); sh=sh.filter(ImageFilter.GaussianBlur(34))
    base.paste((4,14,13),(x-60,y-60),sh)
    base.paste(ph,(x,y),ph)
# ---------- texto ----------
def quebra(txt,font,larg):
    d=ImageDraw.Draw(Image.new('L',(1,1))); linhas=[];l=''
    for p in txt.split():
        t=(l+' '+p).strip()
        if d.textlength(t,font=font)<=larg: l=t
        else: linhas.append(l); l=p
    linhas.append(l); return linhas
_tc={}
def legenda_img(eyebrow, titulo, larg=920):
    k=(eyebrow,titulo)
    if k in _tc: return _tc[k]
    fe=fnt(INTER_SB,31); ft=fnt(SERIF,62,600)
    ls=quebra(titulo,ft,larg); h=60+len(ls)*78+20
    im=Image.new('RGBA',(W,h+40),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.text((80,0),eyebrow.upper(),font=fe,fill=MINT); d.rounded_rectangle((80,52,140,58),radius=3,fill=OCRE)
    y=84
    for ln in ls:
        d.text((83,y+3),ln,font=ft,fill=(0,0,0,90)); d.text((80,y),ln,font=ft,fill='white'); y+=78
    _tc[k]=im; return im
def cola_legenda(base, eyebrow, titulo, t_rel, y=150):
    im=legenda_img(eyebrow,titulo); k=ease(t_rel/0.45)
    a=im.copy(); al=a.getchannel('A').point(lambda v: int(v*k)); a.putalpha(al)
    base.paste(a,(0,int(y+40*(1-k))),a)
def topo_escuro(base, h=560):
    g=Image.new('L',(1,h)); 
    for y in range(h): g.putpixel((0,y), int(200*(1-y/h)**1.4))
    g=g.resize((W,h)); base.paste((10,34,32),(0,0),g)
# ---------- barra de progresso e capítulos ----------
TOTAL=86.4
CAPS=[(15.6,'01'),(30.0,'02'),(39.6,'03'),(55.2,'04'),(63.6,'05'),(70.8,'06')]
def hud(base,t):
    d=ImageDraw.Draw(base)
    d.rectangle((0,0,W,9),fill=(20,52,49)); d.rectangle((0,0,int(W*t/TOTAL),9),fill=OCRE)
    if 15.6<=t<80.4:
        f=fnt(INTER_B,26); x=W-80-6*58
        for i,(ti,n) in enumerate(CAPS):
            on = t>=ti and (i==len(CAPS)-1 or t<CAPS[i+1][0]); past=t>=ti
            c = OCRE if on else ((120,165,155) if past else (60,100,94))
            d.rounded_rectangle((x+i*58,40,x+i*58+48,76),radius=8,fill=(255,255,255,0) if not on else (60,48,30),outline=c,width=2)
            tw=d.textlength(n,font=f); d.text((x+i*58+24-tw/2,43),n,font=f,fill=c)
# ---------- cenas ----------
def cena_hook(t):
    im=FUNDO.copy(); d=ImageDraw.Draw(im)
    f1=fnt(SERIF,66,500); f2=fnt(SERIF,96,700); fi=fnt(SERIF_I,96,600)
    l1=['O','site','que','você','usava','para','buscar','material…']
    ls=quebra(' '.join(l1),f1,900); y=600; wi=0
    for ln in ls:
        x=90
        for w_ in ln.split():
            k=ease((t-0.12*wi)/0.35); 
            if k>0:
                col=tuple(int(c*k+ (0x1A,0x49,0x45)[j]*(1-k)) for j,c in enumerate(CREME))
                d.text((x,y+20*(1-k)),w_,font=f1,fill=col)
            x+=d.textlength(w_+' ',font=f1); wi+=1
        y+=86
    if t>2.3:
        k=ease((t-2.3)/0.5); y2=y+60
        d.text((90,y2+40*(1-k)),'agora virou uma',font=f2,fill=tuple(int(255*k+0x1A*(1-k)) for _ in range(3)))
        k2=ease((t-2.65)/0.5)
        if k2>0:
            d.text((90,y2+118+40*(1-k2)),'plataforma',font=fi,fill=OCRE)
            d.text((90,y2+236+40*(1-k2)),'de estudos.',font=f2,fill='white')
            k3=ease((t-3.2)/0.6); d.rounded_rectangle((92,y2+225,92+int(560*k3),y2+233),radius=4,fill=OCRE)
    return im
def cena_home(t, dur):
    im=FUNDO.copy(); src=SEG['home']+t*(7.3/dur)
    z=1.0+0.06*ease_io(t/dur)
    celular(im, tela(src), W//2, 1130, z)
    topo_escuro(im,620)
    if t<2.9: cola_legenda(im,'Apresentando','Arquivo Vivo, a nova versão',t)
    else: cola_legenda(im,'Tudo num lugar só','Materiais, prazos, resumos e simulados das disciplinas',t-2.9)
    return im
def cena_numeros(t):
    im=FUNDO.copy(); d=ImageDraw.Draw(im)
    fe=fnt(INTER_SB,32); d.text((90,300),'O QUE TEM DENTRO',font=fe,fill=MINT); d.rounded_rectangle((90,352,150,358),radius=3,fill=OCRE)
    itens=[(688,'questões de simulado'),(506,'termos no glossário'),(54,'exercícios interativos'),(23,'resumos com revisão'),(12,'disciplinas, do 1º e do 2º semestre')]
    fn=fnt(SERIF,120,600); fl=fnt(INTER_M,40)
    for i,(n,lab) in enumerate(itens):
        k=ease((t-0.25-i*0.42)/0.5)
        if k<=0: continue
        y=430+i*250+30*(1-k); v=int(n*ease((t-0.25-i*0.42)/0.9))
        col=tuple(int(c*k+(0x1A,0x49,0x45)[j]*(1-k)) for j,c in enumerate((255,255,255)))
        d.text((90,y),str(v),font=fn,fill=OCRE if i==0 else col)
        d.text((90,y+150),lab,font=fl,fill=tuple(int(c*k+(0x1A,0x49,0x45)[j]*(1-k)) for j,c in enumerate(CREME)))
    return im
def cena_capitulo(t, num, titulo, sub):
    im=FUNDO.copy(); d=ImageDraw.Draw(im); k=ease(t/0.4)
    fn=fnt(SERIF,260,600); ft=fnt(SERIF,84,600); fs=fnt(INTER_M,40)
    d.text((86,560+60*(1-k)),num,font=fn,fill=OCRE)
    y=900
    for ln in quebra(titulo,ft,900): d.text((90,y+40*(1-k)),ln,font=ft,fill='white'); y+=100
    d.text((90,y+20),sub,font=fs,fill=MINT)
    return im
def cena_gravada(t, dur, a, b, plano):
    # plano: lista de (t_ini, eyebrow, titulo, zoom, focy)
    im=FUNDO.copy(); src=a+t*((b-a)/dur)
    atual=plano[0]
    for p in plano:
        if t>=p[0]: atual=p
    i=plano.index(atual); prox=plano[i+1][0] if i+1<len(plano) else dur
    z0=plano[i-1][3] if i>0 else 1.0; f0=plano[i-1][4] if i>0 else None
    k=ease_io((t-atual[0])/0.7)
    z=z0+(atual[3]-z0)*k
    fa = atual[4] if atual[4] is not None else 780
    fb = f0 if f0 is not None else 780
    focy=fb+(fa-fb)*k
    cy = 1160 if z<=1.02 else 1180
    celular(im, tela(src), W//2, cy - (focy-780)*SCALE*0 , z, focy)
    topo_escuro(im,640)
    cola_legenda(im, atual[1], atual[2], t-atual[0])
    return im
def cena_fim(t):
    im=FUNDO.copy(); d=ImageDraw.Draw(im)
    f1=fnt(SERIF,70,500); f2=fnt(SERIF_I,92,600); f3=fnt(INTER_SB,40); f4=fnt(INTER_M,36)
    k1=ease(t/0.5); d.text((90,520+30*(1-k1)),'Não é mais um',font=f1,fill=tuple(int(c*k1+(0x1A,0x49,0x45)[j]*(1-k1)) for j,c in enumerate(CREME)))
    d.text((90,610+30*(1-k1)),'site de estudos.',font=f1,fill=tuple(int(c*k1+(0x1A,0x49,0x45)[j]*(1-k1)) for j,c in enumerate(CREME)))
    k2=ease((t-0.9)/0.6)
    if k2>0:
        d.text((90,760+30*(1-k2)),'É a plataforma',font=f2,fill=OCRE); d.text((90,870+30*(1-k2)),'da turma.',font=f2,fill=OCRE)
    k3=ease((t-2.0)/0.6)
    if k3>0:
        logo=Image.open('/home/claude/painel-psicologia/icons/icon-256.png').convert('RGBA').resize((130,130),Image.LANCZOS)
        m=Image.new('L',(130,130),0); ImageDraw.Draw(m).rounded_rectangle((0,0,130,130),radius=30,fill=int(255*k3))
        im.paste(logo,(90,1120),m)
        d.text((250,1135),'Arquivo Vivo',font=fnt(SERIF,58,600),fill='white')
        d.text((252,1205),'Psicologia · 1º e 2º semestre',font=f4,fill=MINT)
    k4=ease((t-2.7)/0.6)
    if k4>0:
        d.rounded_rectangle((90,1330,990,1440),radius=22,fill=(214,158,82))
        tx='Crie sua conta e escolha seu semestre'; tw=d.textlength(tx,font=f3); d.text(((W-tw)/2,1363),tx,font=f3,fill=(40,28,10))
        tx='academicopsi.github.io/Painel-Psicologia'; tw=d.textlength(tx,font=f4); d.text(((W-tw)/2,1480),tx,font=f4,fill=CREME)
    return im

# ---------- notificações (tela de bloqueio) ----------
NOTIFS=[('Psiu! Em 3 dias: Prova N2 de Neuroanatomia','Três dias: um resumo por dia e um simulado no fim. Topa?'),
        ('Psiu! Amanhã: Prova N2 de Desenvolvimento Adulto e Idoso','Respira, revisa o resumo e dorme cedo. Eu acredito em você!'),
        ('Arquivo Vivo','Resumos novos do 1º semestre no ar. Bora conferir?')]
_lock=None
def lock_fundo():
    global _lock
    if _lock is None:
        im=Image.new('RGB',(780,1560)); d=ImageDraw.Draw(im)
        for y in range(1560):
            t=y/1560; d.line([(0,y),(780,y)],fill=tuple(int(a+(b-a)*t) for a,b in zip((0x2B,0x55,0x6E),(0x12,0x1C,0x2E))))
        g=Image.new('L',(780,1560),0); ImageDraw.Draw(g).ellipse((-200,900,700,1800),fill=90); g=g.filter(ImageFilter.GaussianBlur(120)); im.paste((0x3E,0x8E,0x82),(0,0),g)
        d=ImageDraw.Draw(im); fd=fnt(INTER_SB,30); fh=fnt(INTER_B,170)
        tx='sábado, 21 de novembro'; d.text(((780-d.textlength(tx,font=fd))/2,170),tx,font=fd,fill=(235,240,245))
        tx='18:07'; d.text(((780-d.textlength(tx,font=fh))/2,205),tx,font=fh,fill=(240,244,248))
        _lock=im
    return _lock
ICON=Image.open('/home/claude/painel-psicologia/icons/icon-256.png').convert('RGBA').resize((76,76),Image.LANCZOS)
IM=Image.new('L',(76,76),0); ImageDraw.Draw(IM).rounded_rectangle((0,0,76,76),radius=18,fill=255)
def card_notif(titulo, corpo):
    ft=fnt(INTER_B,29); fb=fnt(INTER_M,28); fa=fnt(INTER_M,23)
    lt=quebra(titulo,ft,560); lb=quebra(corpo,fb,560); h=34+len(lt)*36+len(lb)*35+30
    c=Image.new('RGBA',(720,h),(0,0,0,0)); d=ImageDraw.Draw(c)
    d.rounded_rectangle((0,0,719,h-1),radius=34,fill=(245,245,247,232))
    c.paste(ICON,(24,28),IM)
    d.text((616,30),'agora',font=fa,fill=(120,120,128))
    y=26
    for ln in lt: d.text((122,y),ln,font=ft,fill=(20,20,24)); y+=36
    for ln in lb: d.text((122,y),ln,font=fb,fill=(55,55,62)); y+=35
    return c
_cards=None
def cena_notif(t, dur):
    global _cards
    if _cards is None: _cards=[card_notif(a,b) for a,b in NOTIFS]
    scr=lock_fundo().copy(); y=520
    # cada nova notificação entra por cima e empurra as anteriores
    chegadas=[0.5,2.4,4.3]
    vis=[i for i,c in enumerate(chegadas) if t>=c]
    for ordem,i in enumerate(reversed(vis)):
        c=_cards[i]; k=ease((t-chegadas[i])/0.45)
        yy=y if ordem==0 else y
        if ordem==0: yy=int(y-(c.size[1]+40)*(1-k)); a=k
        else:
            yy=y; a=1
        if a<1:
            c2=c.copy(); c2.putalpha(c2.getchannel('A').point(lambda v:int(v*a))); scr.paste(c2,(30,yy),c2)
        else: scr.paste(c,(30,yy),c)
        y=yy+c.size[1]+16 if ordem==0 else y+c.size[1]+16
    im=FUNDO.copy(); z=1.0+0.05*ease_io(t/dur)
    celular(im, scr, W//2, 1180, z)
    topo_escuro(im,640)
    if t<3.6: cola_legenda(im,'Notificações','Lembretes de prova e avisos da turma no seu celular',t)
    else: cola_legenda(im,'Notificações','Chegam mesmo com o site fechado. Você escolhe o que receber.',t-3.6)
    return im
# ---------- linha do tempo ----------
S=SEG
AREA=[(0,'Área logada','A contagem regressiva até a sua próxima prova',1.32,300),
      (1.5,'Guia de estudos','Um plano do dia que se monta sozinho, ou do seu jeito',1.0,None),
      (7.3,'Treinar','Discursiva com correção e revisão dos seus erros',1.0,None),
      (9.4,'Progresso','Veja o quanto você já estudou em cada disciplina',1.0,None)]
APOIO=[(0,'Para apoiadores','Seu desempenho por tema e o que revisar primeiro',1.0,None),
       (4.4,'Para apoiadores','Seu semestre em números, pronto para o story',1.0,None),]
PSIU=[(0,'Psiu, o colega virtual','Pergunte: ele sabe as datas, os prazos e os conceitos',1.0,None),
      (7.5,'Psiu, o colega virtual','E também sabe descontrair',1.0,None)]
SIM=[(0,'Simulados','Escolha o tema, responda e veja a explicação na hora',1.0,None)]
P1=[(0,'1º período','Vai ter aula das disciplinas do 1º período? Vocês não ficaram de fora!',1.0,None)]
CENAS=[('hook',4.8,lambda t:cena_hook(t)),
 ('home',6.0,lambda t:cena_home(t,6.0)),
 ('numeros',4.8,lambda t:cena_numeros(t)),
 ('c1',1.2,lambda t:cena_capitulo(t,'01','Sua área de estudos','Feita para você estudar todo dia')),
 ('area',13.2,lambda t:cena_gravada(t,13.2,S['area_topo'],S['apoio'],AREA)),
 ('c2',1.2,lambda t:cena_capitulo(t,'02','Área do apoiador','Recursos extras para quem apoia')),
 ('apoio',8.4,lambda t:cena_gravada(t,8.4,S['apoio'],S['psiu'],APOIO)),
 ('c3',1.2,lambda t:cena_capitulo(t,'03','Conheça o Psiu','O colega virtual da turma')),
 ('psiu',14.4,lambda t:cena_gravada(t,14.4,S['psiu'],S['sim']-1.6,PSIU)),
 ('c4',1.2,lambda t:cena_capitulo(t,'04','Notificações','O site agora te avisa')),
 ('notif',7.2,lambda t:cena_notif(t,7.2)),
 ('c5',1.2,lambda t:cena_capitulo(t,'05','Simulados','688 questões, separadas por tema')),
 ('sim',6.0,lambda t:cena_gravada(t,6.0,S['sim'],S['p1']-0.3,SIM)),
 ('c6',1.2,lambda t:cena_capitulo(t,'06','1º período','Vocês não ficaram de fora')),
 ('p1',8.4,lambda t:cena_gravada(t,8.4,S['p1'],S['fim'],P1)),
 ('fim',6.0,lambda t:cena_fim(t))]
def render(nome):
    inicio=0
    for n,dur,fn in CENAS:
        if n==nome: break
        inicio+=dur
    dur,fn=[(d,f) for n,d,f in CENAS if n==nome][0]
    tmp=f'/tmp/vid/ed/{nome}.tmp.mp4'
    pr=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r','30','-i','-','-c:v','libx264','-crf','19','-preset','veryfast','-pix_fmt','yuv420p',tmp],stdin=subprocess.PIPE)
    n=round(dur*FPS)
    for i in range(n):
        t=i/FPS; im=fn(t); hud(im,inicio+t)
        if i<4: im=Image.blend(FUNDO,im,(i+1)/5)
        pr.stdin.write(im.tobytes())
    pr.stdin.close(); assert pr.wait()==0; os.replace(tmp,f'/tmp/vid/ed/{nome}.mp4'); print(nome,'ok',flush=True)
if __name__=='__main__':
    os.makedirs('/tmp/vid/ed',exist_ok=True)
    if sys.argv[1]=='frame':
        nome=sys.argv[2]; t=float(sys.argv[3]); inicio=0
        for n,dur,fn in CENAS:
            if n==nome: im=fn(t); hud(im,inicio+t); im.save(sys.argv[4],quality=88); break
            inicio+=dur
    else:
        for nome in sys.argv[1:]: render(nome)
