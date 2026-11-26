exec(open('/tmp/vid/mock_firebase.py').read().split('from playwright')[0])
from playwright.sync_api import sync_playwright
import json, os, shutil, time, base64
OUT='/tmp/vid/rec'; shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT)
frames=[]; segs=[]
SEED = r"""(()=>{
  const sims = SIM_JOGO.filter(s => DISC['2'].some(d => d.n === s.disc));
  const o = {sims:{}, hist:[]}; let seed = 7; const rnd = () => (seed = (seed * 9301 + 49297) % 233280) / 233280;
  sims.forEach((s, k) => { const st = o.sims[s.id] = {}; let a = 0, n = 0;
    s.questoes.slice(0, 30).forEach(q => { const tema = q.tema || 'Geral'; const t = st[tema] = st[tema] || {a:0, n:0}; const ok = rnd() < [0.82, 0.71, 0.88, 0.64, 0.77][k % 5]; t.n++; n++; if(ok){ t.a++; a++; } });
    o.hist.push({id:s.id, pct:Math.round(a / n * 100), a, n, seq:6, t:Date.now() - (5 - k) * 86400000}); });
  localStorage.setItem('av-desempenho', JSON.stringify(o));
  Object.entries(RESUMOS).filter(([, r]) => DISC['2'].some(d => d.n === r.disc)).forEach(([id, r], i) => { const st = {}; r.caps.forEach((c, j) => { if((i + j) % 3 !== 2){ st[c.id] = {}; c.etapas.forEach((e, k) => st[c.id][k] = 1); } }); localStorage.setItem('av-resumo-' + id, JSON.stringify(st)); });
  localStorage.setItem('av-tempo', JSON.stringify({total: 19 * 3600 + 1200, dias:{}}));
})()"""
MURAL_SEED = r"""(()=>{
  const d = JSON.parse(sessionStorage.getItem('fakeDB') || '{"apoiadores/u1":{"ate":1898000000000,"conf":1},"acesso/u1":true}'), h = Date.now(), m = 60000;
  const put = (k, v) => d[k] = v;
  put('perfis/u1', {nome:'Ana Clara', sem:'2', ap:true});
  put('perfis/t1', {nome:'Bruno Lima', sem:'2', ap:true, conq:6, conqT:15}); put('perfis/t2', {nome:'Carla Souza', sem:'2', conq:9, conqT:15});
  put('perfis/t3', {nome:'Diego Alves', sem:'1', conq:3, conqT:15}); put('perfis/t4', {nome:'Júlia Ramos', sem:'2', conq:11, conqT:15});
  put('mural/posts/x1', {uid:'u1', nome:'Ana Clara', titulo:'Quem topa revisar Neuro na segunda depois da aula?', cat:'provas', texto:'Pensei em 1 hora na biblioteca, cada um leva um tema dos nervos cranianos. Quem vem?', em:h-95*m});
  put('mural/posts/x2', {uid:'t1', nome:'Bruno Lima', titulo:'Mapa mental das fases do luto', cat:'materiais', texto:'Montei um resumo visual de Kübler-Ross para a prova de Idoso. Alguém confere se ficou certo?', em:h-40*m});
  put('mural/posts/x3', {uid:'t3', nome:'Diego Alves', titulo:'O simulado de Experimental ajudou demais', cat:'opiniao', texto:'Errei bastante no começo e acertei quase tudo na segunda vez.', em:h-26*60*m});
  put('mural/comentarios/x1/k1', {uid:'t4', nome:'Júlia Ramos', texto:'Eu vou! Fico com o trigêmeo e o facial.', em:h-80*m});
  put('mural/comentarios/x1/k2', {uid:'t1', nome:'Bruno Lima', texto:'@Júlia levo o vago então.', men:['t4'], em:h-60*m});
  put('mural/curtidas/x1/t1', {t:'concordo', em:h-70*m}); put('mural/curtidas/x1/t4', {t:'amei', em:h-75*m});
  put('mural/curtidas/x2/t2', {t:'psiu', em:h-30*m}); put('mural/curtidas/x2/t4', {t:'curtir', em:h-20*m});
  put('mural/curtidas/x3/t1', {t:'haha', em:h-600*m}); put('mural/curtidas/x3/t2', {t:'amei', em:h-500*m});
  sessionStorage.setItem('fakeDB', JSON.stringify(d)); localStorage.setItem('av-mural-ok', '1');
})()"""
# grava como se fosse uma noite de semana antes das provas N2, para o plano e os prazos aparecerem cheios
DATA_FIXA = r"""(()=>{const off=new Date('2026-11-17T19:30:00-03:00').getTime()-Date.now(); const D=Date;
  class F extends D{constructor(...a){ if(a.length) super(...a); else super(D.now()+off); } static now(){ return D.now()+off; }}
  window.Date=F; })()"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--force-device-scale-factor=2'])   # sem isto o screencast sai em 390×780
    ctx=b.new_context(viewport={'width':390,'height':780}, device_scale_factor=2, service_workers='block'); pg=ctx.new_page()
    errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
    def r(route, _q=None):
        u=route.request.url; route.fulfill(status=200, content_type='application/javascript', body=APP if 'firebase-app' in u else AUTH if 'firebase-auth' in u else DB)
    pg.route('**/firebasejs/**', r)
    pg.add_init_script("localStorage.setItem('av-convite-2026-2b','1')"); pg.add_init_script(DATA_FIXA); pg.goto('http://localhost:8765/#entrar');pg.wait_for_timeout(1500)
    pg.fill('#cEmail','ana.clara@exemplo.com');pg.fill('#cSenha','123456');pg.click('[data-form] button[type=submit]'); pg.wait_for_timeout(4000)
    pg.evaluate(SEED)
    pg.evaluate(MURAL_SEED)
    pg.reload(); pg.wait_for_timeout(4000)
    pg.add_style_tag(content="::-webkit-scrollbar{display:none} #psiuBalao{display:none!important} .ma-2ch{display:none!important} html{scroll-behavior:auto}")
    cdp=ctx.new_cdp_session(pg)
    def onf(ev):
        i=len(frames); f=f'{OUT}/{i:05d}.jpg'; open(f,'wb').write(base64.b64decode(ev['data']))
        frames.append([f, ev['metadata']['timestamp']])
        try: cdp.send('Page.screencastFrameAck', {'sessionId': ev['sessionId']})
        except Exception as e: pass
    cdp.on('Page.screencastFrame', onf)
    cdp.send('Page.startScreencast', {'format':'jpeg','quality':90,'maxWidth':780,'maxHeight':1560,'everyNthFrame':1})
    W=lambda ms: pg.wait_for_timeout(ms)
    def seg(n): segs.append([n, time.time()])
    def suave(y, ms=900):
        pg.evaluate("""([y,ms])=>{const y0=scrollY,t0=performance.now();const f=t=>{const k=Math.min(1,(t-t0)/ms),e=k<.5?2*k*k:1-Math.pow(-2*k+2,2)/2;scrollTo(0,y0+(y-y0)*e);if(k<1)requestAnimationFrame(f)};requestAnimationFrame(f)}""", [y, ms]); W(ms+120)
    def ate(sel, off=120, ms=900):
        y=pg.evaluate(f"(()=>{{const e=document.querySelector('{sel}');return e?e.getBoundingClientRect().top+scrollY-{off}:scrollY}})()"); suave(y, ms)
    def toque(sel, idx=0, espera=600):
        el=pg.query_selector_all(sel)[idx]; el.scroll_into_view_if_needed(); bb=el.bounding_box()
        pg.evaluate("""([x,y])=>{const d=document.createElement('div');d.className='vt';d.style.cssText=`position:fixed;left:${x-24}px;top:${y-24}px;width:48px;height:48px;border-radius:50%;background:rgba(201,143,69,.5);border:2px solid #fff;z-index:99999;pointer-events:none;transform:scale(.4);opacity:0;transition:transform .18s,opacity .18s`;document.body.appendChild(d);requestAnimationFrame(()=>{d.style.transform='scale(1)';d.style.opacity='1'});setTimeout(()=>{d.style.opacity='0';d.style.transform='scale(1.4)'},380);setTimeout(()=>d.remove(),700)}""", [bb['x']+bb['width']/2, bb['y']+bb['height']/2])
        W(260); el.click(); W(espera)
    def digita(sel, txt):
        pg.click(sel)
        for ch in txt: pg.keyboard.type(ch); W(55)
    def rola(dy, ms=900):
        pg.evaluate("""([dy,ms])=>{const f0=document.getElementById('benFundo');const y0=f0.scrollTop,t0=performance.now();const f=t=>{const k=Math.min(1,(t-t0)/ms),e=k<.5?2*k*k:1-Math.pow(-2*k+2,2)/2;f0.scrollTop=y0+dy*e;if(k<1)requestAnimationFrame(f)};requestAnimationFrame(f)}""", [dy, ms]); W(ms+120)
    # HOME
    pg.evaluate("location.hash='#top'"); W(800); pg.evaluate("scrollTo(0,0)"); W(300)
    seg('home'); W(900); suave(560, 1500); W(500); suave(1150, 1300); W(500); suave(0, 1000); W(300)
    # ÁREA + PLANO
    pg.evaluate("switchPage('viewHoje')"); W(700); pg.evaluate("scrollTo(0,0)"); W(200)
    seg('area_topo'); W(1500)
    seg('plano_card'); ate('.pg', 80, 900); W(900)
    toque('.pg-tarefas .hj-item input', espera=900)
    seg('plano_abre'); toque('.pg-mais', espera=1600)
    seg('plano_dias'); toque('[data-pl-sel]', idx=1, espera=900); toque('[data-pl-sel]', idx=2, espera=900)
    rola(380, 900); W(300); toque('.pl4-chk', espera=900)
    seg('plano_radar'); rola(560, 1000); W(1100)
    seg('plano_ajuste'); pg.evaluate("document.getElementById('benFundo').scrollTop=0"); W(200); toque('.pl4-aj', espera=900)
    rola(260, 700); toque('[data-pl-foco=meu]', espera=700); toque('[data-pl-disc]', idx=1, espera=450); toque('[data-pl-disc]', idx=4, espera=500)
    toque('[data-pl-minb="60"]', espera=600); toque('[data-pl-pronto]', espera=1500)
    seg('plano_fim'); pg.keyboard.press('Escape'); W(500)
    # APOIADOR: desempenho e story
    pg.evaluate("scrollTo(0,0)"); W(200)
    seg('apoio'); ate('.ma-abas', 70, 600); toque('[data-ma-aba="ferramentas"]', espera=1200)
    toque('[data-ben="desempenho"]', espera=1500)
    rola(300, 1000); W(600)
    pg.keyboard.press('Escape'); W(400)
    seg('story'); toque('[data-ben="semestre"]', espera=2400)
    pg.keyboard.press('Escape'); W(400)
    # PSIU (sem a piada)
    seg('psiu'); pg.evaluate("location.hash='#top'"); W(700); pg.evaluate("scrollTo(0,0)"); W(300)
    toque('#botFab', espera=900)
    digita('#botInput', 'Quando é a prova de neuro?'); pg.keyboard.press('Enter'); W(2700)
    digita('#botInput', 'O que é reforço negativo?'); pg.keyboard.press('Enter'); W(3200)
    pg.click('#botFechar'); W(300)
    # MURAL
    pg.evaluate("location.hash='#top'"); W(500); pg.evaluate("scrollTo(0,0)"); W(300)
    seg('mural'); W(400); toque('.tabbar [data-page="viewMural"], .tabbar [data-tb="mural"]', espera=1800)
    ate('.mu-feed', 230, 1100); W(900)
    toque('[data-mu-ver=x1] .mu-card-t', espera=1300)
    seg('mural_reac'); toque('[data-mu-reagir=x1]', espera=900); toque('[data-mu-reac="x1|psiu"]', espera=1000)
    seg('mural_marca'); ate('.mu-thread', 120, 800)
    pg.click('[data-mu-comentar] textarea'); W(200)
    for ch in 'Valeu, @Ju': pg.keyboard.type(ch); W(70)
    W(900); toque('[data-mu-sug]', espera=400)
    for ch in 'levo o resumo do vago!': pg.keyboard.type(ch); W(45)
    W(300); toque('[data-mu-comentar] button[type=submit]', espera=1300)
    seg('mural_fim')
    # SIMULADO
    pg.evaluate("location.hash='#disc-02'"); W(1600); ate('.sim-card', 260, 10); W(300)
    seg('sim'); W(600); toque('[data-sim-parte-ini]', idx=1, espera=900); toque('[data-sim-start]', espera=1200)
    ci=pg.evaluate("(()=>{const e=simEst,it=e.fila[e.pos];return it.ordem.indexOf(e.sim.questoes[it.i].c)})()")
    toque('#simOverlay [data-sim-op]', idx=ci, espera=2400)
    pg.keyboard.press('Escape'); pg.evaluate("document.querySelector('#simOverlay [data-sim-sair], #simOverlay .sim-x')?.click()"); W(400)
    # 1º PERÍODO
    pg.evaluate("location.hash='#top'"); W(700); pg.evaluate("scrollTo(0,0)"); W(200); ate('#heroSem', 300, 10); W(300)
    seg('p1'); W(700); toque('[data-hero-sem]', espera=2600); ate('#disciplinas', 70, 900); W(1300)
    pg.evaluate("location.hash='#disc-16'"); W(1800); pg.evaluate("scrollTo(0,0)"); W(600); suave(900, 1800); W(700)
    seg('fim'); W(300)
    cdp.send('Page.stopScreencast'); W(300)
    json.dump({'frames':frames,'segs':segs}, open('/tmp/vid/rec.json','w'))
    # PDF do simulado (o arquivo de verdade que o apoiador baixa)
    pg.evaluate("location.hash='#top'"); W(600); pg.evaluate("window.print=()=>{}")
    pg.evaluate("localStorage.setItem('av-semestre','2'); switchPage('viewHoje')"); W(600)
    pg.click('[data-ma-aba="ferramentas"]'); W(600); pg.click('[data-ben="simpdf"]'); W(600)
    pg.click('[data-ben-disc="02"]'); W(600); pg.click('[data-spdf]'); W(800)
    pg.emulate_media(media='print'); pg.pdf(path='/tmp/vid/simulado.pdf', format='A4', print_background=True); pg.emulate_media(media='screen')
    print(len(frames), 'frames', [(s[0], round(s[1]-segs[0][1],1)) for s in segs], 'errs', errs[:3]); b.close()
