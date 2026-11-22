# Trilha "convidativa": pop acústico e ensolarado, 108 bpm, Ré maior (D–A–Bm–G com sus), violão dedilhado,
# piano nos contratempos, palmas e estalos, baixo redondo, glockenspiel no gancho e "uuh" de coro.
import json, os
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt, lfilter, fftconvolve
SR=44100; BPM=108; BEAT=60/BPM; BAR=4*BEAT; S16=BEAT/4
_tp=json.load(open('/tmp/vid/tempos.json')) if os.path.exists('/tmp/vid/tempos.json') else {'total':101.2,'fim':95.2,'caps':[],'t0':4.8}
T0=_tp['t0']; FIM=_tp['fim']; DUR=_tp['total']+2.4; CAPS=_tp['caps']
N=int(SR*DUR); L=np.zeros(N); R=np.zeros(N); RV=np.zeros(N); SC=np.ones(N)
rng=np.random.default_rng(11)
NT={'C':0,'C#':1,'D':2,'D#':3,'E':4,'F':5,'F#':6,'G':7,'G#':8,'A':9,'A#':10,'B':11}
def mi(s): return 12*(int(s[-1])+1)+NT[s[:-1]]
def hz(m): return 440*2**((m-69)/12)
def lp(x,fc,o=2): return sosfilt(butter(o,min(fc/(SR/2),0.99),output='sos'),x)
def hp(x,fc,o=2): return sosfilt(butter(o,fc/(SR/2),'high',output='sos'),x)
def bp(x,a,b): return sosfilt(butter(2,[a/(SR/2),b/(SR/2)],'band',output='sos'),x)
def add(sig,t,pan=0.0,g=1.0,rv=0.0,duck=True):
    i=int(round(t*SR))
    if i>=N: return
    if i<0: sig=sig[-i:]; i=0
    j=min(N,i+len(sig)); s=sig[:j-i]*g
    if duck: s=s*SC[i:j]
    L[i:j]+=s*np.sqrt(0.5*(1-pan)); R[i:j]+=s*np.sqrt(0.5*(1+pan))
    if rv: RV[i:j]+=s*rv
def bt(b): return T0+b*BEAT
# acordes (Ré maior): D  A/C#  Bm7  Gmaj7, com uma volta para Gsus no fim do bloco
CH=[['D3','A3','D4','F#4','A4'],['C#3','A3','E4','A4','C#5'],['B2','F#3','D4','A4','B4'],['G2','D3','B3','F#4','B4']]
BX=['D2','C#2','B1','G1']
# ---------- instrumentos ----------
def violao(t,m,g=0.11,pan=0.0,dec=0.996):
    f=hz(m); P=int(SR/f); n=int(1.6*SR)
    x=np.zeros(n); x[:P]=lp(rng.standard_normal(P),5000)*0.8
    a=np.zeros(P+2); a[0]=1; a[P]=-dec*0.5; a[P+1]=-dec*0.5
    y=lfilter([1.0],a,x); y=lp(y,4200)*np.minimum(1,np.arange(n)/40)
    add(y,t,pan,g,rv=0.18)
def piano(t,m,dur=0.5,g=0.10,pan=0.0):
    n=int((dur+0.9)*SR); tt=np.arange(n)/SR; f=hz(m); s=np.zeros(n)
    for k,(a,dk) in enumerate([(1,2.2),(0.55,3.4),(0.30,4.6),(0.18,6),(0.1,8),(0.06,10)]):
        s+=a*np.sin(2*np.pi*f*(k+1)*(1+0.0004*k*k)*tt)*np.exp(-tt*dk)
    s*=np.minimum(1,tt/0.004)*np.where(tt>dur,np.exp(-(tt-dur)*9),1)
    s+=0.05*hp(rng.standard_normal(n),2000)*np.exp(-tt*120)
    add(s,t,pan,g,rv=0.3)
def glock(t,m,g=0.09,pan=0.15):
    n=int(1.8*SR); tt=np.arange(n)/SR; f=hz(m)
    s=np.sin(2*np.pi*f*tt)*np.exp(-tt*2.6)+0.4*np.sin(2*np.pi*f*2.76*tt)*np.exp(-tt*6)+0.18*np.sin(2*np.pi*f*5.4*tt)*np.exp(-tt*11)
    s*=np.minimum(1,tt/0.002)
    add(s,t,pan,g,rv=0.45)
    add(s*0.3,t+BEAT*0.75,-pan,g,rv=0.5)
def baixo(t,m,dur,g=0.22):
    n=int((dur+0.05)*SR); tt=np.arange(n)/SR; f=hz(m)
    s=np.sin(2*np.pi*f*tt)+0.25*np.sin(2*np.pi*2*f*tt)+0.08*np.sin(2*np.pi*3*f*tt)
    env=np.minimum(1,tt/0.008)*np.exp(-tt*1.8)*np.where(tt>dur,np.exp(-(tt-dur)*40),1)
    add(np.tanh(s*env*1.3)*0.8,t,0,g)
def coro(t,ch,dur,g=0.05):
    n=int((dur+0.6)*SR); tt=np.arange(n)/SR; s=np.zeros(n)
    for k,nm in enumerate(ch[1:4]):
        f=hz(mi(nm)+12); vib=1+0.005*np.sin(2*np.pi*5*tt+k)
        ph=np.cumsum(f*vib)/SR; w=np.sin(2*np.pi*ph)+0.35*np.sin(4*np.pi*ph)+0.12*np.sin(6*np.pi*ph)
        s+=bp(w,300,2400)
    env=np.minimum(1,tt/0.35)*np.where(tt>dur,np.exp(-(tt-dur)*5),1)
    add(s*env,t,0,g,rv=0.6)
def bumbo(t,g=1.0):
    n=int(0.35*SR); tt=np.arange(n)/SR; f=50+80*np.exp(-tt*30); ph=2*np.pi*np.cumsum(f)/SR
    add(np.sin(ph)*np.exp(-tt*10)*0.4,t,0,g,duck=False)
def palma(t,g=1.0,pan=0.0):
    n=int(0.35*SR); tt=np.arange(n)/SR
    env=sum(np.exp(-np.maximum(tt-o,0)*110)*(tt>=o) for o in (0,0.009,0.019))*0.5+np.exp(-tt*18)*0.4
    add(bp(rng.standard_normal(n)*env,900,6000),t,pan,0.22*g,rv=0.35,duck=False)
def estalo(t,g=1.0):
    n=int(0.12*SR); tt=np.arange(n)/SR
    add(bp(rng.standard_normal(n),1800,5500)*np.exp(-tt*70),t,-0.35,0.2*g,rv=0.3,duck=False)
def chocalho(t,g=1.0):
    n=int(0.09*SR); tt=np.arange(n)/SR
    add(hp(rng.standard_normal(n),6000)*np.sin(np.pi*np.minimum(1,tt/0.09))**2,t,0.4,0.06*g,duck=False)
def brilho(tc,g=0.06):   # transição de capítulo: um "shimmer" de glockenspiel subindo
    for k,nm in enumerate(['A5','D6','F#6','A6']): glock(tc-0.32+k*0.07,mi(nm),g*0.8,0.3-0.2*k)
# ---------- respiração no bumbo ----------
nb=int((FIM-T0)/BEAT)
for k in range(nb):
    i=int(bt(k)*SR); j=min(N,i+int(0.18*SR))
    SC[i:j]=np.minimum(SC[i:j],0.6+0.4*(1-np.exp(-np.arange(j-i)/SR*18)))
# ---------- introdução: violão sozinho e piano suave ----------
ib=BAR*(T0/(2*BAR)) / BAR if T0>0 else 1
for b in range(2):
    t=b*T0/2; ch=CH[b*2%4]; dd=T0/2/8
    for e in range(8): violao(t+e*dd, mi(ch[[0,2,3,4,3,2,1,2][e]]), 0.09, -0.3 if e%2 else 0.3)
    piano(t, mi(ch[3]), T0/2*0.9, 0.05)
# ---------- corpo ----------
HOOK=[[(0,'F#5',1),(1,'A5',1),(2,'D6',2),(4,'C#6',1),(5,'A5',1),(6,'F#5',2)],
      [(0,'E5',1),(1,'A5',1),(2,'C#6',2),(4,'B5',1),(5,'A5',1),(6,'E5',2)],
      [(0,'D5',1),(1,'F#5',1),(2,'B5',2),(4,'A5',1),(5,'F#5',1),(6,'D5',2)],
      [(0,'B4',1),(1,'D5',1),(2,'G5',3),(5,'F#5',1),(6,'E5',2)]]
nbars=int((FIM-T0)/BAR)
for b in range(nbars):
    t=T0+b*BAR; k=b%4; ref=(b//8)%2==1; ch=CH[k]
    # violão dedilhado em semicolcheias (padrão travis)
    pad_=[0,3,1,4,2,3,1,4]
    for q in range(16):
        nm=ch[pad_[q%8]] if q%4 else ch[0 if q%8==0 else 1]
        violao(t+q*S16+rng.random()*0.006, mi(nm), 0.075 if q%4 else 0.10, -0.35 if q%2 else 0.35)
    # piano: acorde nos contratempos
    for q in (1,3):
        for nm in ch[2:5]: piano(t+q*BEAT+BEAT/2, mi(nm)+12, BEAT*0.35, 0.035 if not ref else 0.045, 0.2)
    # baixo: tônica no 1 e 3, passagem no 4
    baixo(t, mi(BX[k]), BEAT*1.8); baixo(t+2*BEAT, mi(BX[k]), BEAT*1.3); baixo(t+3.5*BEAT, mi(BX[k])+7, BEAT*0.45, 0.16)
    # percussão leve: bumbo no 1 e 3 (refrão: os 4), palmas no 2 e 4, estalos e chocalho
    for q in range(4):
        if ref or q in (0,2): bumbo(t+q*BEAT, 0.9 if ref else 0.75)
        if q in (1,3): (palma if ref else estalo)(t+q*BEAT, 1.0)
        for h in (0,1,2,3): chocalho(t+q*BEAT+h*S16, 0.7+0.6*(h==2))
    if ref:
        for (o,m,d) in HOOK[k]: glock(t+o*BEAT/2, mi(m), 0.085)
        if k==0: coro(t, CH[0], BAR*4*0.95)
    elif b%8>=4:
        coro(t, ch, BAR*0.95, 0.03)
    if b%8==7:
        for q in range(4): palma(t+3*BEAT+q*S16, 0.35+0.15*q, 0.2)
for tc in CAPS: brilho(tc)
# final: acorde aberto no violão e no piano, glockenspiel
for k,nm in enumerate(['D3','A3','D4','F#4','A4','D5']):
    violao(FIM+k*0.03, mi(nm), 0.12, -0.4+0.16*k, 0.9985); piano(FIM, mi(nm)+12, 2.0, 0.05)
for k,nm in enumerate(['F#6','A6','D7']): glock(FIM+0.25+k*0.18, mi(nm), 0.07)
bumbo(FIM); palma(FIM,0.8)
# ---------- sala e mixagem ----------
irn=int(1.8*SR); ti=np.arange(irn)/SR
irl=lp(rng.standard_normal(irn)*np.exp(-ti*3.2),7000); irr=lp(rng.standard_normal(irn)*np.exp(-ti*3.2),7000)
irl/=np.sqrt(np.sum(irl**2)); irr/=np.sqrt(np.sum(irr**2))
L+=fftconvolve(RV,irl)[:N]*0.5; R+=fftconvolve(RV,irr)[:N]*0.5
mix=np.stack([hp(L,35),hp(R,35)],1)
mix=np.tanh(mix*1.2)/np.tanh(1.2)
fo=int(3.0*SR); mix[-fo:]*=np.linspace(1,0,fo)[:,None]**1.3
alvo=0.16; rms=np.sqrt(np.mean(mix[int(T0*SR):int(FIM*SR)]**2)); mix*=alvo/rms
pk=np.max(np.abs(mix))
if pk>0.97: mix*=0.97/pk
wavfile.write('/tmp/vid/musica.wav',SR,(mix*32767).astype(np.int16)); print('ok pico', round(float(np.max(np.abs(mix))),3))
