# Trilha lo-fi do vídeo: 78 bpm com swing, piano elétrico com acordes de jazz, baixo, bateria macia e chiado de vinil.
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter, fftconvolve
SR=44100; BPM=78; BEAT=60/BPM; BAR=4*BEAT; DUR=104.7; FIM=96.6; ENTRA=4.8
N=int(SR*DUR); L=np.zeros(N); R=np.zeros(N); RV=np.zeros(N)   # RV: envio para o reverb
rng=np.random.default_rng(11)
def nota(m): return 440*2**((m-69)/12)
def lp(x, fc, o=2): b,a=butter(o, min(fc/(SR/2),0.99)); return lfilter(b,a,x)
def hp(x, fc, o=2): b,a=butter(o, fc/(SR/2), 'high'); return lfilter(b,a,x)
def add(sig, t, pan=0.0, g=1.0, rv=0.0):
    i=int(t*SR)
    if i>=N or i+len(sig)<0: return
    j=min(N,i+len(sig)); s=sig[:j-i]*g
    L[i:j]+=s*(1-max(0,pan)); R[i:j]+=s*(1+min(0,pan))
    if rv: RV[i:j]+=s*rv
# piano elétrico (FM, com tremolo e leve oscilação de fita)
def rhodes(m, dur, vel=1.0):
    n=int((dur+1.2)*SR); t=np.arange(n)/SR; f=nota(m)*(1+0.0015*np.sin(2*np.pi*0.6*t+rng.random()*6))
    ph=2*np.pi*np.cumsum(f)/SR
    idx=(1.6*vel)*np.exp(-t*3.2)+0.25
    s=np.sin(ph+idx*np.sin(ph))
    s+=0.12*np.sin(14*ph)*np.exp(-t*30)*vel          # o "tine" do ataque
    a=np.minimum(1,t/0.004); dec=np.exp(-t*0.9)
    rel=np.where(t>dur, np.exp(-(t-dur)*7), 1.0)
    s*=a*dec*rel*(1+0.12*np.sin(2*np.pi*4.2*t))*vel
    return lp(s, 2600+1400*vel)
def acorde(t, notas, dur, g=0.16):
    for k,m in enumerate(notas):
        add(rhodes(m, dur, 0.75+0.1*rng.random()), t+k*0.018+rng.random()*0.006, pan=-0.3+0.6*k/max(1,len(notas)-1), g=g, rv=0.35)
def baixo(t, m, dur, g=0.26):
    n=int((dur+0.15)*SR); tt=np.arange(n)/SR; f=nota(m)
    s=np.sin(2*np.pi*f*tt)+0.25*np.sin(4*np.pi*f*tt)
    e=np.minimum(1,tt/0.01)*np.exp(-tt*1.1)*np.where(tt>dur,np.exp(-(tt-dur)*25),1)
    add(lp(np.tanh(1.3*s*e),420), t, 0, g)
def bumbo(t, g=1.0):
    n=int(0.45*SR); tt=np.arange(n)/SR; f=48+70*np.exp(-tt*32); ph=2*np.pi*np.cumsum(f)/SR
    s=np.sin(ph)*np.exp(-tt*7.5); s[:80]*=np.linspace(0,1,80)
    add(lp(np.tanh(1.5*s),900), t, 0, 0.55*g)
def caixa(t, g=1.0):
    n=int(0.35*SR); tt=np.arange(n)/SR
    corpo=np.sin(2*np.pi*185*tt)*np.exp(-tt*28)*0.6
    ruido=hp(lp(rng.standard_normal(n),4200),700)*np.exp(-tt*16)
    add(lp(corpo+ruido*0.8,5000), t, 0.05, 0.24*g, rv=0.25)
def chimbal(t, g=1.0):
    n=int(0.07*SR); tt=np.arange(n)/SR; s=hp(rng.standard_normal(n),6500)*np.exp(-tt*60)
    add(lp(s,9000), t, 0.25, 0.07*g)
def ducking(tk):
    # o resto "respira" a cada bumbo (sidechain suave)
    pass
# acordes: Gm9 · C13 · Fmaj9 · Dm9 (ii-V-I-vi em Fá)
CH=[[55,58,62,65,69],[58,62,64,69],[57,60,64,67],[53,57,60,64]]
BX=[43,36,41,38]
LICK=[(0.0,72,0.5),(0.75,74,0.25),(1.0,77,0.75),(2.0,76,0.5),(2.5,74,0.5),(3.0,72,0.9)]
LICK2=[(0.5,81,0.25),(0.75,79,0.25),(1.0,77,0.5),(1.75,74,0.5),(2.5,72,1.2)]
SW=0.62   # swing das colcheias
nbar=int(DUR/BAR)+1; kicks=[]
for b in range(nbar):
    t=b*BAR; k=b%4
    if t>=DUR-0.5: break
    fim=t>=FIM
    # acorde em dois toques (antecipação no "e" do 3)
    if not fim or t<FIM+BAR:
        acorde(t, CH[k], BEAT*2.4)
        acorde(t+BEAT*2.5, CH[k][1:], BEAT*1.3, g=0.11)
    if t>=ENTRA-0.01 and not fim:
        baixo(t, BX[k], BEAT*1.6); baixo(t+BEAT*2.5, BX[k]+(7 if k%2 else 12), BEAT*0.9, 0.2)
        for i in range(4):
            bt=t+i*BEAT
            if i==0 or (i==2 and k%2==1): bumbo(bt); kicks.append(bt)
            if i==2 and k%2==0: bumbo(bt+BEAT*SW, 0.75); kicks.append(bt+BEAT*SW)
            if i in (1,3): caixa(bt+0.012)
            for h in (0, SW):
                chimbal(bt+h*BEAT, (0.9 if h==0 else 0.55)*(0.85+0.3*rng.random()))
        # frase de piano a cada dois compassos
        if b%2==1:
            for (o,m,d) in (LICK if b%4==1 else LICK2):
                add(rhodes(m, d*BEAT, 0.6), t+o*BEAT+rng.random()*0.01, 0.2, 0.10, rv=0.5)
# acorde final, deixado soar
acorde(FIM+0.02, [53,57,60,64,67,72], 5.0, 0.12)
# sidechain suave nos instrumentos
env=np.ones(N)
for tk in kicks:
    i=int(tk*SR); n=int(0.32*SR); j=min(N,i+n)
    if i<N: env[i:j]=np.minimum(env[i:j], 1-0.28*np.exp(-np.arange(j-i)/SR*10))
L*=env; R*=env
# reverb de sala (ruído com decaimento) aplicado ao envio
irn=int(1.8*SR); ti=np.arange(irn)/SR
ir_l=rng.standard_normal(irn)*np.exp(-ti*3.2); ir_r=rng.standard_normal(irn)*np.exp(-ti*3.2)
ir_l=lp(ir_l,3500); ir_r=lp(ir_r,3500); ir_l/=np.sqrt(np.sum(ir_l**2)); ir_r/=np.sqrt(np.sum(ir_r**2))
L+=fftconvolve(RV,ir_l)[:N]*0.5; R+=fftconvolve(RV,ir_r)[:N]*0.5
# vinil: chiado contínuo e estalos
hiss=lp(hp(rng.standard_normal(N),1500),6000)*0.0035
cr=np.zeros(N); pos=rng.integers(0,N,int(DUR*6)); cr[pos]=rng.standard_normal(len(pos))*0.14
cr=lp(hp(cr,1200),7000)
L+=hiss+cr; R+=hiss*0.9+np.roll(cr,7)
mix=np.stack([L,R],1)
# cara de fita: graves arredondados, agudos domados, saturação leve
mix=np.stack([lp(hp(mix[:,c],35),8500) for c in (0,1)],1)
mix=np.tanh(mix*1.25)/np.tanh(1.25)
# abertura filtrada (só o piano, abafado) e saída suave
fi=int(0.8*SR); mix[:fi]*=np.linspace(0,1,fi)[:,None]
fo=int(4.0*SR); mix[-fo:]*=np.linspace(1,0,fo)[:,None]**1.5
alvo=0.14; rms=np.sqrt(np.mean(mix[int(ENTRA*SR):int(FIM*SR)]**2)); mix*=alvo/rms
pk=np.max(np.abs(mix))
if pk>0.95: mix*=0.95/pk
wavfile.write('/tmp/vid/musica.wav',SR,(mix*32767).astype(np.int16)); print('ok', DUR, 'pico', round(float(np.max(np.abs(mix))),3))
