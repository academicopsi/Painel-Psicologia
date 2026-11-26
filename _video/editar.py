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
        ('Júlia respondeu ao seu tópico','“Quem topa revisar Neuro na segunda?”: Eu vou! Fico com o trigêmeo e o facial.')]
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

# =====================================================================
# V2 do vídeo: telas novas e efeitos (celular em 3D, cartões saltando da tela, Psiu saindo do celular)
# =====================================================================
import numpy as np
REC=json.load(open('/tmp/vid/rec.json')); FR=REC['frames']; FT=[t for _,t in FR]; T0=FT[0]
SEG={n:t-T0 for n,t in REC['segs']}; S=SEG
_cache={}
def tela(ts):
    i=max(0,bisect.bisect_right(FT,ts+T0)-1); f=FR[i][0]
    if f not in _cache:
        if len(_cache)>60: _cache.clear()
        _cache[f]=Image.open(f).convert('RGB')
    return _cache[f]
SCALE=0.84; SW,SH=int(780*SCALE),int(1560*SCALE)
MASK=Image.new('L',(SW,SH),0); ImageDraw.Draw(MASK).rounded_rectangle((0,0,SW,SH),radius=48,fill=255)
PW,PH=SW+32,SH+32
BEZ=Image.new('RGBA',(PW,PH),(0,0,0,0)); ImageDraw.Draw(BEZ).rounded_rectangle((0,0,PW-1,PH-1),radius=62,fill=(13,26,25,255),outline=(70,110,104,255),width=3)
def phone(shot):
    ph=BEZ.copy(); ph.paste(shot.resize((SW,SH),Image.BILINEAR),(16,16),MASK); return ph
def ease_back(k):
    k=max(0,min(1,k)); c=1.6; return 1+(c+1)*(k-1)**3+c*(k-1)**2
def lerp(a,b,k): return a+(b-a)*k
# ---------- 3D ----------
F3=2600
def _pts(w,h,ry,rx,rz,s):
    cr,sr=math.cos(rz),math.sin(rz); out=[]
    def m(x,y):
        x,y=x*cr-y*sr, x*sr+y*cr
        z=x*math.sin(ry); x=x*math.cos(ry)
        y2=y*math.cos(rx)-z*math.sin(rx); z2=y*math.sin(rx)+z*math.cos(rx)
        k=F3/(F3+z2); return (x*k*s, y2*k*s)
    return m
def _coef(dst,src):
    A=[];B=[]
    for (x,y),(u,v) in zip(dst,src):
        A.append([x,y,1,0,0,0,-u*x,-u*y]); B.append(u)
        A.append([0,0,0,x,y,1,-v*x,-v*y]); B.append(v)
    return np.linalg.solve(np.array(A,float),np.array(B,float)).tolist()
def place(base, img, cx, cy, ry=0, rx=0, rz=0, s=1.0, sombra=0.55, alpha=1.0):
    """desenha img (RGBA) com rotação 3D, centro em (cx,cy). Devolve função tela->quadro."""
    w,h=img.size; m=_pts(w,h,math.radians(ry),math.radians(rx),math.radians(rz),s)
    def mapa(u,v): x,y=m(u-w/2,v-h/2); return (cx+x, cy+y)
    q=[m(-w/2,-h/2),m(w/2,-h/2),m(w/2,h/2),m(-w/2,h/2)]
    mx=min(p[0] for p in q); my=min(p[1] for p in q); Mx=max(p[0] for p in q); My=max(p[1] for p in q)
    ow,oh=int(Mx-mx)+2,int(My-my)+2
    dst=[(p[0]-mx,p[1]-my) for p in q]
    if abs(ry)<0.05 and abs(rx)<0.05 and abs(rz)<0.05:
        im=img.resize((max(1,int(w*s)),max(1,int(h*s))),Image.BILINEAR) if abs(s-1)>1e-3 else img
    else:
        im=img.transform((ow,oh),Image.PERSPECTIVE,_coef(dst,[(0,0),(w,0),(w,h),(0,h)]),Image.BICUBIC)
    x0=int(cx+mx); y0=int(cy+my)
    if sombra>0:
        sc=4; pad=60
        sh=Image.new('L',(ow//sc+2*pad//sc+2,oh//sc+2*pad//sc+2),0)
        ImageDraw.Draw(sh).polygon([((p[0])/sc+pad/sc,(p[1])/sc+pad/sc) for p in dst],fill=int(255*sombra*alpha))
        sh=sh.filter(ImageFilter.GaussianBlur(9)).resize(((ow//sc+2*pad//sc+2)*sc,(oh//sc+2*pad//sc+2)*sc),Image.BILINEAR)
        base.paste((3,12,11),(x0-pad+18,y0-pad+46),sh)
    if alpha<1:
        im=im.copy(); im.putalpha(im.getchannel('A').point(lambda v:int(v*alpha)))
    base.paste(im,(x0,y0),im)
    return mapa
def celular3d(base, shot, cx=W//2, cy=1180, ry=0, rx=0, rz=0, s=1.0):
    return place(base, phone(shot), cx, cy, ry, rx, rz, s)
def balanco(t, a=6, b=2.5, per=8.0):
    return a*math.sin(2*math.pi*t/per), b*math.sin(2*math.pi*t/(per*1.37)+1.1)
# cartão recortado da tela, com cantos arredondados
def recorte(shot, box, raio=26):
    c=shot.crop(box).convert('RGBA'); m=Image.new('L',c.size,0); ImageDraw.Draw(m).rounded_rectangle((0,0,c.size[0]-1,c.size[1]-1),radius=raio,fill=255)
    c.putalpha(m); fr=Image.new('RGBA',(c.size[0]+8,c.size[1]+8),(0,0,0,0)); ImageDraw.Draw(fr).rounded_rectangle((0,0,fr.size[0]-1,fr.size[1]-1),radius=raio+4,fill=(255,255,255,235))
    fr.paste(c,(4,4),c); return fr
_rc={}
def salta(base, mapa, ts_src, box, t, t0, t1, alvo, sc, ry=-10, rx=4, rz=-2):
    """cartão que sai da tela do celular em 3D e volta"""
    if t<t0 or t>t1: return 0
    k_in=ease_back((t-t0)/0.75); k_out=ease_io((t1-t)/0.55) if t>t1-0.55 else 1
    k=min(k_in,k_out)
    key=(ts_src,box)
    if key not in _rc: _rc[key]=recorte(tela(ts_src),box)
    card=_rc[key]
    ox,oy=mapa(16+(box[0]+box[2])/2*SCALE, 16+(box[1]+box[3])/2*SCALE)
    s0=SCALE*0.98
    cx=lerp(ox,alvo[0],k); cy=lerp(oy,alvo[1],k); s=lerp(s0,sc,k)
    # escurece o fundo para destacar
    if k>0.01:
        ov=Image.new('L',base.size,int(110*min(1,k))); base.paste((6,22,20),(0,0),ov)
    place(base, card, cx, cy, ry*k, rx*k, rz*k, s, sombra=0.6*k)
    return k
# ---------- legendas por tempo ----------
def legenda_em(base, plano, t, y=150):
    atual=plano[0]
    for p in plano:
        if t>=p[0]: atual=p
    cola_legenda(base, atual[1], atual[2], t-atual[0], y)
def srcm(a,b,dur): return lambda t: a+t*((b-a)/dur)
def ts(nome,dt=0.0): return S[nome]+dt
def cena_t(a,b,dur,tsrc): return (tsrc-a)*dur/(b-a)   # tempo de origem -> tempo da cena
# ---------- cenas ----------
def cena_home(t, dur):
    im=FUNDO.copy(); src=S['home']+t*(7.3/dur)
    k=ease(t/1.3); ry=lerp(55,-6,k)+2*math.sin(t*1.2)*(k); rx=lerp(10,2,k); s=lerp(0.75,1.0,k)
    celular3d(im, tela(src), W//2, 1190, ry, rx, 0, s)
    topo_escuro(im,620)
    if t<2.7: cola_legenda(im,'Apresentando','Arquivo Vivo, a nova versão',t)
    else: cola_legenda(im,'Tudo num lugar só','Materiais, prazos, resumos e simulados das disciplinas',t-2.7)
    return im
PL_A,PL_B,PL_D=S['plano_card'],S['plano_fim'],17.0
def plt(n,dt=0): return cena_t(PL_A,PL_B,PL_D,S[n]+dt)
PLANO=[(0,'Plano de hoje','Seu plano do dia já vem pronto quando você entra'),
       (plt('plano_abre',0.4),'Plano de estudos','A semana inteira num painel só'),
       (plt('plano_dias'),'Sua semana','Toque no dia e marque o que já estudou'),
       (plt('plano_radar'),'Provas no radar','Quanto falta e quanto da preparação já foi feita'),
       (plt('plano_ajuste'),'Do seu jeito','Escolha as disciplinas, o tempo por dia e os dias de estudo')]
def cena_plano(t):
    im=FUNDO.copy(); src=PL_A+t*((PL_B-PL_A)/PL_D)
    a,b=balanco(t,7,2.5,9)
    mapa=celular3d(im, tela(src), W//2, 1190, a, b)
    topo_escuro(im,640)
    # números do painel saltam da tela
    t0=plt('plano_abre',1.5); salta(im,mapa,ts('plano_abre',1.5),(36,385,744,735),t,t0,t0+2.6,(540,1090),1.32,ry=-16,rx=8,rz=-3)
    t0=plt('plano_dias',0.15); salta(im,mapa,ts('plano_dias',0.15),(24,1040,760,1215),t,t0,t0+1.9,(540,1180),1.36,ry=14,rx=10,rz=3)
    legenda_em(im,PLANO,t)
    return im
def cena_pdf(t, dur):
    im=FUNDO.copy(); shot=tela(ts('apoio',2.2))
    k=ease(t/0.8); ry=lerp(0,24,k)+2*math.sin(t*1.3); cx=lerp(W//2,330,k)
    mapa=celular3d(im, shot, cx, 1200, ry, 3, 0, lerp(1.0,0.86,k))
    topo_escuro(im,600)
    cola_legenda(im,'Simulado em PDF','Prova sorteada para imprimir, com gabarito na última folha',t)
    ox,oy=mapa(16+390*SCALE, 16+1190*SCALE)
    alvos=[((690,1000),-6,-22),((810,1150),6,-16),((730,1320),-2,-12)]
    for i,(pg_,(alvo,rz,ry_)) in reversed(list(enumerate(zip(PAGS,alvos)))):
        t0=0.7+i*0.42; kk=ease_back((t-t0)/0.9)
        if t<t0: continue
        fl=4*math.sin((t-t0)*1.6+i)
        place(im, pg_, lerp(ox,alvo[0],kk), lerp(oy,alvo[1],kk)+fl*(kk), ry_*kk, 6*kk, rz*kk, lerp(0.12,1.0,kk), sombra=0.55)
    return im
PAGS=[]
def _pags():
    import glob
    fs=sorted(glob.glob('/tmp/vid/pdfh-*.png'))
    for f in [fs[0],fs[1],fs[-1]]:
        p=Image.open(f).convert('RGBA'); p=p.resize((600,int(600*p.size[1]/p.size[0])),Image.LANCZOS)
        PAGS.append(p)
_pags()
AP_A,AP_B,AP_D=S['apoio']+1.0,S['psiu']-0.2,9.0
APOIO=[(0,'Seu desempenho','Acertos por tema e o que revisar primeiro'),
       (cena_t(AP_A,AP_B,AP_D,S['story']),'Seu semestre em números','Pronto para salvar e comparar com os seus dados no futuro')]
def cena_apoio(t):
    im=FUNDO.copy(); src=AP_A+t*((AP_B-AP_A)/AP_D)
    a,b=balanco(t,-7,2,8)
    mapa=celular3d(im, tela(src), W//2, 1190, a, b)
    topo_escuro(im,640)
    t0=cena_t(AP_A,AP_B,AP_D,S['story']+1.4); salta(im,mapa,ts('story',1.4),(88,528,692,1560),t,t0,AP_D+1,(560,1220),0.98,ry=-18,rx=6,rz=-4)
    legenda_em(im,APOIO,t)
    return im
PSIU=Image.open('/tmp/vid/psiu.png').convert('RGBA')
_psc={}
def psiu_img(larg):
    larg=int(larg)
    if larg not in _psc:
        if len(_psc)>80: _psc.clear()
        _psc[larg]=PSIU.resize((larg,int(larg*PSIU.size[1]/PSIU.size[0])),Image.LANCZOS)
    return _psc[larg]
def balao(base, x, y, txt, k):
    if k<=0: return
    f=fnt(INTER_B,38); d=ImageDraw.Draw(Image.new('L',(1,1))); tw=d.textlength(txt,font=f)
    b=Image.new('RGBA',(int(tw)+70,120),(0,0,0,0)); dd=ImageDraw.Draw(b)
    dd.rounded_rectangle((0,0,b.size[0]-1,92),radius=30,fill=(255,255,255,245)); dd.polygon([(40,88),(70,88),(30,118)],fill=(255,255,255,245))
    dd.text((35,22),txt,font=f,fill=(30,60,56))
    place(base,b,x+b.size[0]/2,y,0,0,-3*(1-k),lerp(0.4,1,ease_back(k)),sombra=0.3,alpha=min(1,k*2))
PS_A,PS_B,PS_D=S['psiu'],S['mural']-0.2,10.5
PSIUL=[(0,'Conheça o Psiu','O colega virtual da turma pula da tela para te ajudar'),
       (3.2,'Pergunte ao Psiu','Datas das provas, prazos e conceitos das aulas')]
def cena_psiu(t):
    im=FUNDO.copy(); src=PS_A+t*((PS_B-PS_A)/PS_D)
    a,b=balanco(t,6,2,9)
    mapa=celular3d(im, tela(src), W//2+70, 1190, a, b)
    topo_escuro(im,640); legenda_em(im,PSIUL,t)
    # Psiu sai do botão no canto da tela
    ox,oy=mapa(16+688*SCALE,16+1462*SCALE)
    k=ease_back((t-0.25)/0.9)
    if t>=0.25:
        larg=lerp(70,400,k) if t<2.6 else lerp(400,300,ease_io((t-2.6)/0.8))
        cx=lerp(ox,250,k) if t<2.6 else lerp(250,190,ease_io((t-2.6)/0.8))
        cy=lerp(oy,1290,k) if t<2.6 else lerp(1290,1650,ease_io((t-2.6)/0.8))
        bob=math.sin(t*3.2)*10*k; rz=lerp(25,-6,k)+math.sin(t*2.1)*4
        sq=1+0.06*math.sin(t*6.4)*max(0,1-(t-1.1)) if t>1.1 else 1
        p=psiu_img(larg)
        place(im,p.resize((p.size[0],int(p.size[1]*sq))),cx,cy+bob,ry=-8*k,rx=0,rz=rz,s=1.0,sombra=0.4)
        if 1.0<t<3.0: balao(im, cx+60, cy-larg*0.62, 'Psiu! Pode perguntar.', min(1,(t-1.0)/0.4)*(1 if t<2.6 else max(0,(3.0-t)/0.4)))
    return im
MU_A,MU_B,MU_D=S['mural'],S['mural_fim'],11.0
MURAL=[(0,'Corredor da turma','Tópicos com título e categoria, sempre com o seu nome'),
       (cena_t(MU_A,MU_B,MU_D,S['mural_reac']),'Reações','Curtir, Concordo, Haha, Amei e o Psiu'),
       (cena_t(MU_A,MU_B,MU_D,S['mural_marca']),'Marque colegas','Digite @ e a pessoa recebe uma notificação')]
def cena_mural(t):
    im=FUNDO.copy(); src=MU_A+t*((MU_B-MU_A)/MU_D)
    a,b=balanco(t,-6,2,8.5)
    celular3d(im, tela(src), W//2, 1190, a, b)
    topo_escuro(im,640); legenda_em(im,MURAL,t); return im
def cena_rec(a,b_,dur,plano,sinal=1):
    def f(t):
        im=FUNDO.copy(); src=a+t*((b_-a)/dur)
        x,y=balanco(t,6*sinal,2,8)
        celular3d(im, tela(src), W//2, 1190, x, y)
        topo_escuro(im,640); legenda_em(im,plano,t); return im
    return f
# ---------- notificações ----------
NOTIFS=[('Psiu! Aviso da turma','A prova de Neuro foi adiada para quinta. Bora aproveitar para revisar!'),
        ('Júlia respondeu ao seu tópico','“Quem topa revisar Neuro na segunda?”: Eu vou! Fico com o trigêmeo e o facial.'),
        ('Bruno marcou você no Corredor','“@Ana levo o resumo do vago!”')]
_lock=None
def lock_fundo():
    global _lock
    if _lock is None:
        im=Image.new('RGB',(780,1560)); d=ImageDraw.Draw(im)
        for y in range(1560):
            tt=y/1560; d.line([(0,y),(780,y)],fill=tuple(int(a+(b-a)*tt) for a,b in zip((0x2B,0x55,0x6E),(0x12,0x1C,0x2E))))
        g=Image.new('L',(780,1560),0); ImageDraw.Draw(g).ellipse((-200,900,700,1800),fill=90); g=g.filter(ImageFilter.GaussianBlur(120)); im.paste((0x3E,0x8E,0x82),(0,0),g)
        d=ImageDraw.Draw(im); fd=fnt(INTER_SB,30); fh=fnt(INTER_B,170)
        tx='segunda-feira, 23 de novembro'; d.text(((780-d.textlength(tx,font=fd))/2,170),tx,font=fd,fill=(235,240,245))
        tx='19:30'; d.text(((780-d.textlength(tx,font=fh))/2,205),tx,font=fh,fill=(240,244,248))
        _lock=im
    return _lock
_cards=None
def cena_notif(t, dur):
    global _cards
    if _cards is None: _cards=[card_notif(a,b) for a,b in NOTIFS]
    chegadas=[0.6,2.4,4.2]
    scr=lock_fundo().copy(); y=520; ys={}
    vis=[i for i,c in enumerate(chegadas) if t>=c+0.55]
    for i in reversed(vis):
        scr.paste(_cards[i],(30,y),_cards[i]); ys[i]=y; y+=_cards[i].size[1]+16
    im=FUNDO.copy(); ry=lerp(-22,10,ease_io(t/dur)); rx=4
    mapa=celular3d(im, scr, W//2, 1200, ry, rx)
    topo_escuro(im,640)
    if t<3.4: cola_legenda(im,'Avisos no celular','Os avisos da turma chegam na hora, mesmo com o site fechado',t)
    else: cola_legenda(im,'Avisos no celular','E você fica sabendo quando respondem ou marcam você no Corredor',t-3.4)
    # cada notificação chega grande, na frente, e entra no celular
    for i,c in enumerate(chegadas):
        if c<=t<c+0.6:
            k=ease_io((t-c)/0.6); dx,dy=mapa(16+(30+360)*SCALE,16+(520+_cards[i].size[1]/2)*SCALE)
            place(im,_cards[i],lerp(540,dx,k),lerp(760,dy,k),lerp(-8,ry,k),lerp(10,rx,k),lerp(-3,0,k),lerp(1.32,SCALE,k),sombra=0.5)
    return im
SIM=[(0,'Simulados','Escolha o tema, responda e veja a explicação na hora')]
P1=[(0,'1º período','Vai ter aula das disciplinas do 1º período? Vocês não ficaram de fora!')]
TOTAL=None
CAPS=[]
CENAS=[('hook',4.8,lambda t:cena_hook(t)),
 ('home',5.4,lambda t:cena_home(t,5.4)),
 ('numeros',4.5,lambda t:cena_numeros(t)),
 ('c1',1.0,lambda t:cena_capitulo(t,'01','Plano de estudos','Pronto sozinho ou do seu jeito')),
 ('plano',PL_D,lambda t:cena_plano(t)),
 ('c2',1.0,lambda t:cena_capitulo(t,'02','Simulado em PDF','Para imprimir, com gabarito')),
 ('pdf',6.0,lambda t:cena_pdf(t,6.0)),
 ('c3',1.0,lambda t:cena_capitulo(t,'03','Seu desempenho','E o seu semestre em números')),
 ('apoio',AP_D,lambda t:cena_apoio(t)),
 ('c4',1.0,lambda t:cena_capitulo(t,'04','Conheça o Psiu','O colega virtual da turma')),
 ('psiu',PS_D,lambda t:cena_psiu(t)),
 ('c5',1.0,lambda t:cena_capitulo(t,'05','Corredor da turma','Conversa, materiais e elogios')),
 ('mural',MU_D,lambda t:cena_mural(t)),
 ('c6',1.0,lambda t:cena_capitulo(t,'06','Avisos no celular','O site agora te avisa')),
 ('notif',7.0,lambda t:cena_notif(t,7.0)),
 ('c7',1.0,lambda t:cena_capitulo(t,'07','Simulados','688 questões, separadas por tema')),
 ('sim',6.0,cena_rec(S['sim'],S['p1']-0.3,6.0,SIM)),
 ('c8',1.0,lambda t:cena_capitulo(t,'08','1º período','Vocês não ficaram de fora')),
 ('p1',7.0,cena_rec(S['p1'],S['fim'],7.0,P1,-1)),
 ('fim',6.0,lambda t:cena_fim(t))]
_ini=0
for n,dur,_ in CENAS:
    if n.startswith('c') and n[1:].isdigit(): CAPS.append((_ini,n[1:].zfill(2)))
    if n=='fim': FIM=_ini
    _ini+=dur
TOTAL=_ini
def hud(base,t):
    d=ImageDraw.Draw(base)
    d.rectangle((0,0,W,9),fill=(20,52,49)); d.rectangle((0,0,int(W*t/TOTAL),9),fill=OCRE)
    if CAPS[0][0]<=t<FIM:
        f=fnt(INTER_B,24); x=W-70-len(CAPS)*54
        for i,(ti,n) in enumerate(CAPS):
            on = t>=ti and (i==len(CAPS)-1 or t<CAPS[i+1][0]); past=t>=ti
            c = OCRE if on else ((120,165,155) if past else (60,100,94))
            d.rounded_rectangle((x+i*54,40,x+i*54+44,74),radius=8,fill=None if not on else (60,48,30),outline=c,width=2)
            tw=d.textlength(n,font=f); d.text((x+i*54+22-tw/2,43),n,font=f,fill=c)
def render(nome):
    inicio=0
    for n,dur,fn in CENAS:
        if n==nome: break
        inicio+=dur
    dur,fn=[(d,f) for n,d,f in CENAS if n==nome][0]
    tmp=f'/tmp/vid/ed/{nome}.tmp.mp4'
    pr=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r','30','-i','-','-c:v','libx264','-crf','20','-preset','veryfast','-pix_fmt','yuv420p',tmp],stdin=subprocess.PIPE)
    n=round(dur*FPS)
    for i in range(n):
        t=i/FPS; im=fn(t); hud(im,inicio+t)
        if i<4: im=Image.blend(FUNDO,im,(i+1)/5)
        pr.stdin.write(im.tobytes())
    pr.stdin.close(); assert pr.wait()==0; os.replace(tmp,f'/tmp/vid/ed/{nome}.mp4'); print(nome,'ok',flush=True)
if __name__=='__main__':
    os.makedirs('/tmp/vid/ed',exist_ok=True)
    if sys.argv[1]=='tempos':
        json.dump({'total':TOTAL,'fim':FIM,'caps':[c for c,_ in CAPS],'t0':CENAS[0][1]},open('/tmp/vid/tempos.json','w')); print(TOTAL,FIM,CAPS)
    elif sys.argv[1]=='frame':
        nome=sys.argv[2]; inicio=0
        for n,dur,fn in CENAS:
            if n==nome:
                for k,tt in enumerate(sys.argv[3].split(',')):
                    im=fn(float(tt)); hud(im,inicio+float(tt)); im.save(f'/tmp/vid/fr_{nome}_{k}.jpg',quality=85)
                break
            inicio+=dur
    else:
        for nome in sys.argv[1:]: render(nome)
