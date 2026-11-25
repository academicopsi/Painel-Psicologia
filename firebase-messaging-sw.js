// Arquivo Vivo · service worker
// 1) guarda uma cópia do site para abrir sem internet (sempre tenta a internet primeiro)
// 2) recebe as notificações com o site fechado
const CACHE = 'av-offline-v2';
const BASE = new URL(self.registration.scope).pathname;          // /Painel-Psicologia/
const ESSENCIAIS = ['', 'icons/icon-192.png', 'icons/icon-180.png', 'manifest.webmanifest'].map(x => BASE + x);

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => Promise.all(ESSENCIAIS.map(u => c.add(new Request(u, {cache:'reload'})).catch(() => {})))).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => e.waitUntil((async () => {
  for(const k of await caches.keys()) if(k.startsWith('av-offline-') && k !== CACHE) await caches.delete(k);
  await self.clients.claim();
})()));

const EXTERNOS = u => u.hostname === 'fonts.googleapis.com' || u.hostname === 'fonts.gstatic.com' || (u.hostname === 'www.gstatic.com' && u.pathname.startsWith('/firebasejs/'));
const comLimite = (p, ms) => new Promise((ok, erro) => { const t = setTimeout(() => erro(new Error('lento')), ms); p.then(r => { clearTimeout(t); ok(r); }, x => { clearTimeout(t); erro(x); }); });

self.addEventListener('fetch', e => {
  const r = e.request; if(r.method !== 'GET') return;
  const u = new URL(r.url);
  if(EXTERNOS(u)){
    // fontes e bibliotecas: usa a cópia guardada e só baixa se não tiver
    e.respondWith(caches.open(CACHE).then(async c => (await c.match(r)) || fetch(r).then(resp => { if(resp.ok || resp.type === 'opaque') c.put(r, resp.clone()); return resp; })));
    return;
  }
  if(u.origin !== location.origin || !u.pathname.startsWith(BASE) || u.pathname.endsWith('firebase-messaging-sw.js')) return;
  // arquivos do site: internet primeiro; sem sinal (ou muito lento), a cópia guardada
  const chave = new Request(u.origin + u.pathname);
  const pagina = r.mode === 'navigate';
  e.respondWith((async () => {
    const c = await caches.open(CACHE);
    try{
      const resp = await comLimite(fetch(r, pagina ? {cache:'no-cache'} : undefined), pagina ? 7000 : 15000);
      if(resp.ok) c.put(chave, resp.clone());
      return resp;
    }catch(_){
      const guardado = await c.match(chave) || (pagina && (await c.match(new Request(u.origin + u.pathname.replace(/index\.html$/, '')))));
      if(guardado) return guardado;
      return new Response('<meta charset="utf-8"><meta name="viewport" content="width=device-width"><p style="font-family:sans-serif;padding:24px">Sem internet e esta página ainda não foi guardada no aparelho. Abra o Arquivo Vivo uma vez com internet para ele funcionar offline.</p>', {status:503, headers:{'Content-Type':'text/html; charset=utf-8'}});
    }
  })());
});

self.addEventListener('push', e => {
  let d = {};
  try{ d = e.data ? e.data.json() : {}; }catch(_){ d = {notification:{title:'Arquivo Vivo', body: e.data ? e.data.text() : ''}}; }
  const n = d.notification || {}, extra = d.data || {};
  const titulo = n.title || extra.titulo || 'Arquivo Vivo';
  const op = {
    body: n.body || extra.mensagem || '',
    icon: 'icons/icon-192.png',
    badge: 'icons/icon-192.png',
    tag: extra.tag || undefined,
    data: {link: extra.link || (d.fcmOptions && d.fcmOptions.link) || './'}
  };
  e.waitUntil(self.registration.showNotification(titulo, op));
});

self.addEventListener('notificationclick', e => {
  e.notification.close();
  const alvo = new URL(e.notification.data && e.notification.data.link || './', self.registration.scope).href;
  e.waitUntil((async () => {
    const abertas = await self.clients.matchAll({type:'window', includeUncontrolled:true});
    for(const c of abertas){ if(c.url.startsWith(self.registration.scope)){ await c.focus(); if('navigate' in c) try{ await c.navigate(alvo); }catch(_){} return; } }
    await self.clients.openWindow(alvo);
  })());
});
