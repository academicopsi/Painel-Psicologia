import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter
SR=44100; BPM=100; BEAT=60/BPM; BAR=4*BEAT; DUR=79.5
N=int(SR*DUR); L=np.zeros(N); R=np.zeros(N)
rng=np.random.default_rng(3)
def nota(m): return 440*2**((m-69)/12)
def add(sig, t, pan=0.0, g=1.0):
    i=int(t*SR); j=min(N,i+len(sig)); 
    if i>=N: return
    s=sig[:j-i]*g; L[i:j]+=s*(1-max(0,pan)); R[i:j]+=s*(1+min(0,pan))
def env(n, a, d, s, r, sus):
    t=np.arange(n)/SR; e=np.ones(n)*s
    ai=int(a*SR); di=int(d*SR); e[:ai]=np.linspace(0,1,ai) if ai else e[:ai]
    if di: e[ai:ai+di]=np.linspace(1,s,len(e[ai:ai+di]))
    ri=int(r*SR); si=int(sus*SR)
    if si<n: e[si:]=s*np.exp(-np.arange(n-si)/SR/max(r,1e-3)*4)
    return e
def lp(x, fc, o=2): b,a=butter(o, min(fc/(SR/2),0.99)); return lfilter(b,a,x)
def hp(x, fc, o=2): b,a=butter(o, fc/(SR/2), 'high'); return lfilter(b,a,x)
# progressão A  E  F#m  D
CH=[[57,61,64],[52,56,59],[54,57,61],[50,54,57]]
RAIZ=[45,40,42,38]
def pad(t, ch, dur, g):
    n=int(dur*SR); tt=np.arange(n)/SR; s=np.zeros(n)
    for m in ch:
        for det in (-0.08,0.0,0.08):
            f=nota(m+12)*2**(det/12); ph=rng.random()*6.28
            s+= (2*((tt*f+ph/6.28)%1)-1)*0.5 + np.sin(2*np.pi*f*tt+ph)*0.5
    s=lp(s,1800,2)*env(n,0.35,0.3,0.8,0.6,dur-0.2)/9
    add(s,t,0,g)
def pluck(t, m, g, pan):
    n=int(0.5*SR); tt=np.arange(n)/SR; f=nota(m)
    s=(np.sin(2*np.pi*f*tt)+0.35*np.sin(4*np.pi*f*tt)+0.12*np.sin(6*np.pi*f*tt))*np.exp(-tt*7)
    s[:200]*=np.linspace(0,1,200); add(s,t,pan,g)
def baixo(t, m, dur, g):
    n=int(dur*SR); tt=np.arange(n)/SR; f=nota(m)
    s=np.tanh(1.6*(np.sin(2*np.pi*f*tt)+0.3*np.sin(4*np.pi*f*tt)))*env(n,0.005,0.1,0.75,0.08,dur-0.06)
    add(lp(s,700),t,0,g)
def bumbo(t,g=1):
    n=int(0.4*SR); tt=np.arange(n)/SR; f=45+80*np.exp(-tt*28); ph=2*np.pi*np.cumsum(f)/SR
    s=np.sin(ph)*np.exp(-tt*9); s[:60]*=np.linspace(0,1,60); add(s,t,0,0.95*g)
def palma(t,g=1):
    n=int(0.25*SR); tt=np.arange(n)/SR; s=rng.standard_normal(n)
    s=hp(lp(s,3500),900)*(np.exp(-tt*22)+0.4*np.exp(-np.maximum(tt-0.012,0)*30)*(tt>0.012))
    add(s,t,0,0.32*g)
def chimbal(t,g=1,aberto=False):
    n=int((0.18 if aberto else 0.05)*SR); tt=np.arange(n)/SR; s=hp(rng.standard_normal(n),7000)*np.exp(-tt*(14 if aberto else 70))
    add(s,t,0.2,0.12*g)
def impacto(t):
    n=int(1.6*SR); tt=np.arange(n)/SR; s=hp(rng.standard_normal(n),3000)*np.exp(-tt*3.2)*0.22
    add(s,t,0,1); bumbo(t,1.1)
def subida(t0,t1):
    n=int((t1-t0)*SR); tt=np.linspace(0,1,n); s=rng.standard_normal(n)
    out=np.zeros(n); blk=2048
    for i in range(0,n,blk):
        fc=600+9000*tt[i]**2; out[i:i+blk]=lp(s[i:i+blk],fc,2)
    add(out*tt**2*0.22,t0,0,1)
# estrutura
nbar=int(DUR/BAR)+1
for b in range(nbar):
    t=b*BAR; k=b%4; ch=CH[k]
    if t>=DUR-1: break
    fim = t>=72.0
    pad(t, ch, BAR+0.3, 0.55 if b>=2 else 0.4+0.08*b)
    # arpejo
    padrao=[0,1,2,1,0,2,1,2]
    for i in range(8):
        tt=t+i*BEAT/2
        m=ch[padrao[i]]+12+(12 if i in (5,7) else 0)
        g=0.10 if b<2 else 0.13
        if fim: g*=max(0,1-(tt-72)/5.5)
        pluck(tt,m,g,-0.35 if i%2 else 0.35)
    if 2<=b and not fim:
        r=RAIZ[k]
        for i,(o,d) in enumerate([(0,0.55),(0.75,0.25),(1.5,0.5),(2.5,0.4),(3.25,0.6)]):
            baixo(t+o*BEAT, r+(12 if i==3 else 0), d, 0.5)
        for i in range(4):
            if i in (0,2) or (i==3 and k==3): bumbo(t+i*BEAT + (0.5*BEAT if i==3 else 0))
            if i in (1,3): palma(t+i*BEAT)
        for i in range(8): chimbal(t+i*BEAT/2, 1.0 if i%2 else 0.6, aberto=(i==7))
subida(2.4,4.8)
for tc in (4.8,15.6,30.0,39.6,55.2,62.4,72.0): impacto(tc)
subida(70.8,72.0)
# acorde final
pad(72.0,[57,61,64,69],6.0,0.6)
mix=np.stack([L,R],1)
# compressão suave e normalização
mix=np.tanh(mix*1.4)/np.tanh(1.4)
fade=np.ones(N); fs=int(2.5*SR); fade[-fs:]=np.linspace(1,0,fs); mix*=fade[:,None]
mix/=np.max(np.abs(mix))*1.12
wavfile.write('/tmp/vid/musica.wav',SR,(mix*32767).astype(np.int16)); print('ok', DUR)
