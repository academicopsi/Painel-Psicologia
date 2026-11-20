// Envia notificações do Arquivo Vivo pelo Firebase Cloud Messaging.
// Modos:
//   aviso      → mensagem escrita (arquivo notificacoes/*.json ou disparo manual)
//   lembretes  → todo dia: provas e entregas de amanhã, e provas em 3 dias
import fs from 'node:fs';
import vm from 'node:vm';
import admin from 'firebase-admin';

const SA = process.env.FIREBASE_SERVICE_ACCOUNT;
if(!SA){ console.log('Segredo FIREBASE_SERVICE_ACCOUNT ainda não configurado. Nada enviado.'); process.exit(0); }
admin.initializeApp({ credential: admin.credential.cert(JSON.parse(SA)), databaseURL: 'https://arquivo-vivo-psi-default-rtdb.firebaseio.com' });
const db = admin.database();
const ADMIN_EMAIL = 'thiagodentalbeauty@gmail.com';
const SITE = process.env.SITE_ARQUIVO || 'v3/index.html';       // na virada para o oficial: index.html
const BASE = process.env.SITE_URL || 'https://academicopsi.github.io/Painel-Psicologia/v3/';

async function destinos(tipo, publico){
  const pe = (await db.ref('pedidos').get()).val() || {};
  const out = [];
  for(const [uid, p] of Object.entries(pe)){
    const pu = p && p.push; if(!pu || !pu.token) continue;
    if(publico === 'admin' && (pu.email || p.email) !== ADMIN_EMAIL) continue;
    if(tipo === 'provas' && pu.provas === false) continue;
    if(tipo === 'avisos' && pu.avisos === false) continue;
    out.push({uid, token: pu.token});
  }
  return out;
}

async function enviar(lista, titulo, mensagem, link, tag){
  if(!lista.length){ console.log('Ninguém para receber.'); return; }
  const msgs = lista.map(d => ({ token: d.token,
    notification: { title: titulo, body: mensagem },
    data: { titulo, mensagem, link: link || BASE, tag: tag || '' },
    webpush: { fcmOptions: { link: link || BASE }, headers: { Urgency: 'high' } } }));
  for(let i = 0; i < msgs.length; i += 500){
    const r = await admin.messaging().sendEach(msgs.slice(i, i + 500));
    let ok = 0;
    await Promise.all(r.responses.map(async (x, j) => {
      if(x.success){ ok++; return; }
      const cod = x.error && x.error.code;
      console.log('Falhou:', cod);
      if(cod === 'messaging/registration-token-not-registered' || cod === 'messaging/invalid-registration-token'){
        await db.ref('pedidos/' + lista[i + j].uid + '/push').remove();
      }
    }));
    console.log(`Enviadas ${ok} de ${msgs.length}.`);
  }
}

function prazos(){
  const html = fs.readFileSync(SITE, 'utf8');
  const a = html.indexOf('const TASKS = ['); const b = html.indexOf('\n];', a);
  return vm.runInNewContext('(' + html.slice(a + 'const TASKS = '.length, b + 2) + ')');
}
function isoBR(somaDias){ const d = new Date(Date.now() - 3 * 3600e3 + somaDias * 864e5); return d.toISOString().slice(0, 10); }

const modo = process.env.MODO || 'aviso';
if(modo === 'aviso'){
  const arq = process.env.ARQUIVO;
  let p = { titulo: process.env.TITULO, mensagem: process.env.MENSAGEM, link: process.env.LINK, publico: process.env.PUBLICO || 'todos' };
  if(arq){ p = Object.assign({publico:'todos'}, JSON.parse(fs.readFileSync(arq, 'utf8'))); }
  if(!p.mensagem){ console.log('Sem mensagem.'); process.exit(0); }
  await enviar(await destinos('avisos', p.publico), p.titulo || 'Arquivo Vivo', p.mensagem, p.link, p.tag);
} else {
  const amanha = isoBR(1), em3 = isoBR(3);
  const lista = prazos().filter(t => t.prazo === amanha || (t.prazo === em3 && /prova/i.test(t.tarefa)));
  if(!lista.length){ console.log('Nenhum prazo para lembrar hoje.'); process.exit(0); }
  const dest = await destinos('provas', 'todos');
  for(const t of lista){
    const quando = t.prazo === amanha ? 'Amanhã' : 'Em 3 dias';
    const prova = /prova/i.test(t.tarefa);
    await enviar(dest, `${quando}: ${t.tarefa}`, `${t.materia}. ${prova ? 'Que tal um simulado ou uma revisão dos erros hoje?' : 'Não deixe para a última hora.'}`, BASE, 'prazo-' + t.prazo);
  }
}
process.exit(0);
