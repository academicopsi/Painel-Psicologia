APP="export function initializeApp(c){return {c}}"
AUTH="""let cbs=[]; const cb=u=>cbs.forEach(f=>f(u)); const U=()=>JSON.parse(sessionStorage.getItem('fakeUser')||'null');
export function getAuth(){return {}}
export function onAuthStateChanged(a,f){cbs.push(f); setTimeout(()=>f(U()),300)}
export async function signInWithEmailAndPassword(a,e,p){ const u={uid:'u1',email:e,displayName:'Ana Clara'}; sessionStorage.setItem('fakeUser',JSON.stringify(u)); cb(u); return {user:u}}
export async function createUserWithEmailAndPassword(){}
export async function updateProfile(){}
export async function sendPasswordResetEmail(){}
export class GoogleAuthProvider{ setCustomParameters(){} }
export async function signInWithPopup(){ throw {code:"auth/popup-closed-by-user"} }
export async function signInWithRedirect(){}
export async function signOut(){ sessionStorage.removeItem('fakeUser'); cb(null)}"""
DB="""const L=()=>JSON.parse(sessionStorage.getItem('fakeDB')||'{"apoiadores/u1":{"ate":1898000000000,"conf":1},"acesso/u1":true}'); const S=d=>sessionStorage.setItem('fakeDB',JSON.stringify(d));
export function getDatabase(){return {}}
export function ref(d,p){return p}
export async function get(p){ await new Promise(r=>setTimeout(r,200)); const d=L(); if(p==='usuarios/u1' && !sessionStorage.getItem('jaPuxou')){ sessionStorage.setItem('jaPuxou','1'); return {val:()=>({atualizadoEm:Date.now()+5000, progresso:{'av-desempenho':JSON.stringify({sims:{}, hist:[]})}})}; } if(p in d) return {val:()=>d[p]}; const pre=p+'/'; const o={}; Object.keys(d).forEach(k=>{if(k.startsWith(pre)){ const ps=k.slice(pre.length).split('/'); let n=o; ps.slice(0,-1).forEach(x=>{n=n[x]=n[x]||{}}); n[ps[ps.length-1]]=d[k]; }}); return {val:()=>Object.keys(o).length?o:null}}
export async function set(p,v){ await new Promise(r=>setTimeout(r,200)); const d=L(); d[p]=JSON.parse(JSON.stringify(v)); S(d); window.__sets=(window.__sets||0)+1}
export async function remove(p){const d=L(); delete d[p]; S(d)}
export function goOnline(){} export function goOffline(){}"""
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome')
    pg=b.new_page(viewport={'width':390,'height':844})
    errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
    def r(route):
        u=route.request.url; route.fulfill(status=200, content_type='application/javascript', body=APP if 'firebase-app' in u else AUTH if 'firebase-auth' in u else DB)
    pg.route('**/firebasejs/**', r)
    pg.goto('http://localhost:8765/#entrar');pg.wait_for_timeout(1500)
    pg.fill('#cEmail','ana.clara@exemplo.com');pg.fill('#cSenha','123456');pg.click('[data-form] button[type=submit]')
    pg.wait_for_timeout(4500)
    pg.evaluate("""localStorage.setItem('av-erros', JSON.stringify({a:{disc:'05',q:'Q1',ops:['a','b'],c:'a',n:2,t:1,origem:'Simulado'},b:{disc:'05',q:'Q2',ops:['a','b'],c:'a',n:1,t:2,origem:'Simulado'},c:{disc:'02',q:'Q3',ops:['a','b'],c:'a',n:1,t:3,origem:'Quiz'}})); avRenderHoje()""")
    pg.wait_for_timeout(300); pg.evaluate("document.querySelector('.hj-grid').scrollIntoView()"); pg.screenshot(path='/tmp/e1.png')
    pg.click('[data-hj-erros="02"]'); pg.wait_for_timeout(400)
    print(pg.evaluate("document.querySelector('.er-chip.on').textContent"), pg.evaluate("document.querySelectorAll('.er-item').length"))
    print('errs',errs)
    b.close()
