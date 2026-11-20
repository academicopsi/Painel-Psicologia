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
  const comPush = Object.values(pe).filter(p => p && p.push && p.push.token);
  console.log(`::notice::Aparelhos com notificações ativadas: ${comPush.length} (e-mails: ${comPush.map(p => (p.push.email || p.email || '?').replace(/(.).*@/, '$1***@')).join(', ') || 'nenhum'})`);
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
  if(!lista.length){ console.log('::notice::Ninguém para receber (nenhum aparelho ativado para este público).'); return; }
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
      console.log('::warning::Falhou: ' + cod + ' ' + ((x.error && x.error.message) || ''));
      if(cod === 'messaging/registration-token-not-registered' || cod === 'messaging/invalid-registration-token'){
        await db.ref('pedidos/' + lista[i + j].uid + '/push').remove();
      }
    }));
    console.log(`::notice::Enviadas ${ok} de ${msgs.length}.`);
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
  await enviar(await destinos('avisos', p.publico), p.titulo || 'Psiu!', p.mensagem, p.link, p.tag);
} else {
  const amanha = isoBR(1), em3 = isoBR(3);
  const lista = prazos().filter(t => t.prazo === amanha || (t.prazo === em3 && /prova/i.test(t.tarefa)));
  if(!lista.length){ console.log('Nenhum prazo para lembrar hoje.'); process.exit(0); }
  const dest = await destinos('provas', 'todos');
  const um = a => a[Math.floor(Math.random() * a.length)];
  for(const t of lista){
    const prova = /prova/i.test(t.tarefa), amanhaJa = t.prazo === amanha;
    const titulo = `Psiu! ${amanhaJa ? 'Amanhã' : 'Em 3 dias'}: ${t.tarefa} de ${t.materia}`;
    const corpo = prova
      ? (amanhaJa ? um(['Um simulado hoje e você chega tranquilo. Já deixei o café pronto.', 'Bora revisar os erros? Eu seguro o cronômetro.', 'Respira, revisa o resumo e dorme cedo. Eu acredito em você!'])
                  : um(['Ainda dá tempo de estudar com calma. Que tal começar pelo resumo hoje?', 'Três dias: um resumo por dia e um simulado no fim. Topa?']))
      : (amanhaJa ? um(['Já está pronto? Se faltar algo, ainda dá tempo hoje.', 'Não deixa para a madrugada, hein. Eu cochilo e você não!']) : 'Começar hoje deixa tudo mais leve. Bora?');
    await enviar(dest, titulo, corpo, BASE, 'prazo-' + t.prazo + '-' + t.materia);
  }
}
process.exit(0);
