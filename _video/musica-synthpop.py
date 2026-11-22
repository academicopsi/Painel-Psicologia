# Trilha synth-pop alegre (estilo pop anos 80 moderno): 125 bpm, G–D–Em–C, baixo de oitavas, sintetizadores largos e refrão com gancho.
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter, sosfilt, fftconvolve
SR=44100; BPM=125; BEAT=60/BPM; BAR=4*BEAT; S16=BEAT/4
import json, os
# tempos vêm do editar.py (python3 editar.py tempos); sem o arquivo, usa os da primeira versão
_tp=json.load(open('/tmp/vid/tempos.json')) if os.path.exists('/tmp/vid/tempos.json') else {'total':102.6,'fim':96.6,'caps':[15.6,30.0,39.6,55.2,71.4,79.8,87.0],'t0':4.8}
T0=_tp['t0']; FIM=_tp['fim']; DUR=_tp['total']+2.1
CAPS=_tp['caps']
N=int(SR*DUR); L=np.zeros(N); R=np.zeros(N); RV=np.zeros(N); SC=np.ones(N)
rng=np.random.default_rng(7)
def nota(m): return 440*2**((m-69)/12)
NT={'C':0,'C#':1,'D':2,'D#':3,'E':4,'F':5,'F#':6,'G':7,'G#':8,'A':9,'A#':10,'B':11}
def mi(s): n=s[:-1]; o=int(s[-1]); return 12*(o+1)+NT[n]
def sos_lp(fc,o=2): return butter(o,min(fc/(SR/2),0.99),output='sos')
def lp(x,fc,o=2): return sosfilt(sos_lp(fc,o),x)
def hp(x,fc,o=2): return sosfilt(butter(o,fc/(SR/2),'high',output='sos'),x)
def saw(ph): return 2*(ph%1.0)-1
def add(sig,t,pan=0.0,g=1.0,rv=0.0,duck=True):
    i=int(round(t*SR));
    if i>=N: return
    if i<0: sig=sig[-i:]; i=0
    j=min(N,i+len(sig)); s=sig[:j-i]*g
    if duck: s=s*SC[i:j]
    L[i:j]+=s*np.sqrt(0.5*(1-pan)); R[i:j]+=s*np.sqrt(0.5*(1+pan))
    if rv: RV[i:j]+=s*rv
def bt(b): return T0+b*BEAT   # tempo de uma batida (a partir da entrada da bateria)
nbeats=int((FIM-T0)/BEAT)
# sidechain: tudo "respira" no bumbo
for k in range(nbeats):
    i=int(bt(k)*SR); n=int(0.22*SR); j=min(N,i+n)
    SC[i:j]=np.minimum(SC[i:j],0.35+0.65*(1-np.exp(-np.arange(j-i)/SR*22)))
# acordes por compasso: G D Em C
CH=[['G3','B3','D4','G4'],['F#3','A3','D4','A4'],['G3','B3','E4','G4'],['G3','C4','E4','G4']]
BX=['G2','D2','E2','C2']
def supersaw(m,dur,g=1.0):
    n=int((dur+0.25)*SR); t=np.arange(n)/SR; s=np.zeros(n)
    for d in (-0.19,-0.11,-0.04,0,0.05,0.12,0.18):
        f=nota(m)*2**(d/12); s+=saw(f*t+rng.random())
    a=np.minimum(1,t/0.03); r=np.where(t>dur,np.exp(-(t-dur)*14),1)
    return s/7*a*r*g
def pad(t,ch,dur,brilho):
    for k,nm in enumerate(ch):
        s=lp(supersaw(mi(nm),dur),brilho,2)
        add(s,t,pan=(-0.6 if k%2 else 0.6)*(0.4+0.2*k),g=0.12,rv=0.25)
def baixo(t,m,dur,g=0.2):
    n=int((dur+0.03)*SR); tt=np.arange(n)/SR; f=nota(m)
    s=0.7*saw(f*tt)+0.6*np.sin(2*np.pi*f*tt)
    env=np.minimum(1,tt/0.004)*np.exp(-tt*5)*np.where(tt>dur,np.exp(-(tt-dur)*60),1)
    fc=lp_env=300+1600*np.exp(-tt*18)
    out=np.zeros(n); y=0.0; a=1-np.exp(-2*np.pi*fc/SR)
    xs=s*env
    for i in range(n): y+=a[i]*(xs[i]-y); out[i]=y   # filtro que abre e fecha a cada nota
    add(np.tanh(out*1.6)*0.8,t,0,g)
def pluck(t,m,g=0.08,pan=0.0):
    n=int(0.32*SR); tt=np.arange(n)/SR; f=nota(m)
    s=np.sign(np.sin(2*np.pi*f*tt))*0.5+saw(f*1.003*tt)*0.5
    s=lp(s*np.exp(-tt*11),3500)
    add(s,t,pan,g,rv=0.2)
    add(s*0.45,t+BEAT*0.75,-pan,g,rv=0.25)   # eco de colcheia pontuada
def lead(t,m,dur,g=0.17):
    n=int((dur+0.18)*SR); tt=np.arange(n)/SR
    vib=1+0.004*np.sin(2*np.pi*5.5*tt)*np.minimum(1,tt/0.25)
    ph=np.cumsum(nota(m)*vib)/SR
    s=0.55*saw(ph)+0.45*saw(ph*1.006+0.3)+0.25*np.sin(2*np.pi*ph*0.5)
    env=np.minimum(1,tt/0.012)*(0.75+0.25*np.exp(-tt*6))*np.where(tt>dur,np.exp(-(tt-dur)*22),1)
    add(lp(s*env,5200),t,0.05,g,rv=0.35)
    add(lp(s*env,3000)*0.35,t+BEAT*0.5,0.0,g,rv=0.4)
def bumbo(t,g=1.0):
    n=int(0.4*SR); tt=np.arange(n)/SR; f=45+110*np.exp(-tt*38); ph=2*np.pi*np.cumsum(f)/SR
    s=np.sin(ph)*np.exp(-tt*9)+0.3*np.exp(-tt*300)*rng.standard_normal(n)*0.2
    add(np.tanh(1.8*s)*0.42,t,0,g,duck=False)
def palma(t,g=1.0):
    n=int(0.5*SR); tt=np.arange(n)/SR; ru=rng.standard_normal(n)
    env=sum(np.exp(-np.maximum(tt-o,0)*90)*(tt>=o) for o in (0,0.011,0.022))*0.5+np.exp(-tt*14)*0.6
    s=hp(lp(ru*env,7000),900)
    body=np.sin(2*np.pi*190*tt)*np.exp(-tt*30)*0.5
    add(s+body,t,0,0.32*g,rv=0.55,duck=False)
def chimbal(t,aberto=False,g=1.0):
    n=int((0.22 if aberto else 0.05)*SR); tt=np.arange(n)/SR
    s=hp(rng.standard_normal(n),8000)*np.exp(-tt*(14 if aberto else 80))
    add(s,t,0.3,(0.13 if aberto else 0.09)*g,duck=False)
def subida(t1,t2,g=0.12):
    n=int((t2-t1)*SR); tt=np.arange(n)/SR; x=tt/(t2-t1)
    ru=rng.standard_normal(n); out=np.zeros(n); seg=int(SR*0.05)
    for a in range(0,n,seg):
        fc=400+9000*x[a]**2; out[a:a+seg]=hp(ru[a:a+seg],fc,1)
    add(out*x**1.5,t1,0,g,rv=0.3,duck=False)
def whoosh(tc,g=0.09):
    n=int(0.9*SR); tt=np.arange(n)/SR; x=tt/0.9
    s=lp(hp(rng.standard_normal(n),1500),9000)*np.sin(np.pi*x)**2
    add(s,tc-0.6,0,g,rv=0.4,duck=False)
# introdução: acorde abafado subindo até a entrada da bateria
for k in range(3):
    pad(k*BAR*0.833,CH[k%4],BAR*0.833,1400+900*k)
subida(T0-2*BAR*0.833,T0,0.10)
# corpo: estrofe (8 compassos) e refrão (8 compassos) se alternando
HOOK=[[(0,'B4',1),(1,'D5',1),(2,'G5',2),(4,'F#5',1),(5,'E5',1),(6,'D5',2)],
      [(0,'A4',1),(1,'D5',1),(2,'F#5',2),(4,'E5',1),(5,'D5',1),(6,'A4',2)],
      [(0,'B4',1),(1,'E5',1),(2,'G5',2),(4,'F#5',1),(5,'G5',1),(6,'A5',2)],
      [(0,'G5',2),(2,'E5',2),(4,'D5',3),(7,'B4',1)]]
HOOK2=[[(0,'D5',2),(2,'B4',1),(3,'D5',1),(4,'G5',3),(7,'A5',1)],
       [(0,'F#5',2),(2,'D5',1),(3,'F#5',1),(4,'A5',3),(7,'G5',1)],
       [(0,'E5',2),(2,'B4',1),(3,'E5',1),(4,'G5',2),(6,'F#5',1),(7,'E5',1)],
       [(0,'E5',3),(3,'D5',1),(4,'C5',2),(6,'D5',2)]]
nbars=int((FIM-T0)/BAR)
for b in range(nbars):
    t=T0+b*BAR; k=b%4; sec=(b//8)%2   # 0 estrofe, 1 refrão
    pad(t,CH[k],BAR*0.98,2600 if sec==0 else 5200)
    for e in range(8):   # baixo em oitavas, colcheias
        baixo(t+e*BEAT/2, mi(BX[k])+(12 if e%2 else 0), BEAT/2*0.8)
    for q in range(16):   # arpejo
        if sec==0 or q%2==0:
            nn=CH[k][[0,1,2,3,2,1,3,2][q%8]]
            pluck(t+q*S16, mi(nn)+12, 0.075 if sec==0 else 0.06, -0.5 if q%2 else 0.5)
    for q in range(4):
        bumbo(t+q*BEAT)
        if q in (1,3): palma(t+q*BEAT)
        chimbal(t+q*BEAT+BEAT/2,aberto=True)
        for h in (0,2,3) if sec==1 else (0,2):
            chimbal(t+q*BEAT+h*S16,g=0.8+0.4*rng.random())
    if sec==1:
        frase=HOOK if (b//16)%2==0 else HOOK2
        for (o,m,d) in frase[k]: lead(t+o*BEAT/2, mi(m), d*BEAT/2*0.92)
    if b%8==7:   # virada no fim de cada bloco
        for q in range(4): palma(t+3*BEAT+q*S16,0.5+0.15*q)
# transições de capítulo
for tc in CAPS: whoosh(tc)
subida(FIM-BAR,FIM,0.09)
# final: acorde aberto e brilho
for nm in ['G2','G3','B3','D4','G4','B4','D5']:
    add(lp(supersaw(mi(nm),4.5),4000),FIM,0,0.07,rv=0.4,duck=False)
lead(FIM, mi('G5'), 2.4, 0.08)
bumbo(FIM); palma(FIM,0.8)
# reverb de sala grande
irn=int(2.2*SR); ti=np.arange(irn)/SR
irl=lp(rng.standard_normal(irn)*np.exp(-ti*2.6),6000); irr=lp(rng.standard_normal(irn)*np.exp(-ti*2.6),6000)
irl/=np.sqrt(np.sum(irl**2)); irr/=np.sqrt(np.sum(irr**2))
L+=fftconvolve(RV,irl)[:N]*0.45; R+=fftconvolve(RV,irr)[:N]*0.45
mix=np.stack([L,R],1)
mix=np.stack([hp(mix[:,c],30) for c in (0,1)],1)
mix=np.tanh(mix*1.4)/np.tanh(1.4)
fo=int(3.5*SR); mix[-fo:]*=np.linspace(1,0,fo)[:,None]**1.3
alvo=0.17; rms=np.sqrt(np.mean(mix[int(T0*SR):int(FIM*SR)]**2)); mix*=alvo/rms
pk=np.max(np.abs(mix));
if pk>0.97: mix*=0.97/pk
wavfile.write('/tmp/vid/musica.wav',SR,(mix*32767).astype(np.int16)); print('ok pico', round(float(np.max(np.abs(mix))),3))
