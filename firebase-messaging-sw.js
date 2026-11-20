// Arquivo Vivo · recebe as notificações com o site fechado.
// Não guarda nada em cache: só mostra a notificação e abre o site no toque.
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', e => e.waitUntil(self.clients.claim()));

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
