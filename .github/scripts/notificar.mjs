// Envia notificações do Arquivo Vivo pelo Firebase Cloud Messaging.
// Modos:
//   aviso      → mensagem escrita (arquivo notificacoes/*.json ou disparo manual)
//   lembretes  → todo dia: provas e entregas de amanhã, e provas em 3 dias
//   mural      → a cada 5 min: avisos escritos no Painel do administrador, respostas e marcações do mural
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

// lembretes de prazos: uma vez por dia, entre 18h07 e 23h (Brasília), nunca repetidos no mesmo dia
async function lembretes(){
  const agoraBR = new Date(Date.now() - 3 * 3600e3), min = agoraBR.getUTCHours() * 60 + agoraBR.getUTCMinutes(), hoje = isoBR(0);
  if(min < 18 * 60 + 7 || min > 23 * 60){ console.log('Fora do horário dos lembretes (18h07 às 23h).'); return; }
  const marca = db.ref('pedidos/_lembretes/ultimo');
  if((await marca.get()).val() === hoje){ console.log('Lembretes de hoje já enviados.'); return; }
  await marca.set(hoje);
  const amanha = isoBR(1), em3 = isoBR(3);
  const lista = prazos().filter(t => t.prazo === amanha || (t.prazo === em3 && /prova/i.test(t.tarefa)));
  if(!lista.length){ console.log('Nenhum prazo para lembrar hoje.'); return; }
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

const modo = process.env.MODO || 'aviso';
if(modo === 'aviso'){
  const arq = process.env.ARQUIVO;
  let p = { titulo: process.env.TITULO, mensagem: process.env.MENSAGEM, link: process.env.LINK, publico: process.env.PUBLICO || 'todos' };
  if(arq){ p = Object.assign({publico:'todos'}, JSON.parse(fs.readFileSync(arq, 'utf8'))); }
  if(!p.mensagem){ console.log('Sem mensagem.'); process.exit(0); }
  await enviar(await destinos('avisos', p.publico), p.titulo || 'Psiu!', p.mensagem, p.link, p.tag);
} else if(modo === 'mural'){
  await lembretes();
  // avisos escritos no Painel do administrador: fila em pedidos/<uid do administrador>/fila
  {
    let admUid = null;
    try{ admUid = (await admin.auth().getUserByEmail(ADMIN_EMAIL)).uid; }catch(e){ console.log('::warning::Conta do administrador não encontrada: ' + e.message); }
    if(admUid){
      const filaRef = db.ref('pedidos/' + admUid + '/fila'), f = (await filaRef.get()).val() || {};
      for(const [id, a] of Object.entries(f)){
        if(!a || a.status !== 'pendente' || !a.mensagem) continue;
        try{
          const lista = await destinos('avisos', a.publico === 'admin' ? 'admin' : 'todos');
          await enviar(lista, String(a.titulo || 'Psiu!').slice(0, 60), String(a.mensagem).slice(0, 180), BASE + (a.link || ''), 'aviso-' + id);
          await filaRef.child(id).update({status: 'enviado', enviadoEm: Date.now(), n: lista.length});
          console.log(`::notice::Aviso do painel enviado para ${lista.length} aparelho(s).`);
        }catch(e){ await filaRef.child(id).update({status: 'erro', erro: String(e.message || e).slice(0, 200)}); }
      }
    }
  }
  // respostas e marcações do mural: avisa só quem está envolvido (autor do tópico, quem participou, quem foi marcado)
  const marco = db.ref('mural/_push/ultimo'), agora = Date.now(), ultimo = (await marco.get()).val();
  if(!ultimo){ await marco.set(agora); console.log('Marco inicial gravado. A partir de agora as novidades do mural são enviadas.'); process.exit(0); }
  const ler = async c => (await db.ref(c).get()).val() || {};
  const [posts, com, perfis, pe] = await Promise.all([ler('mural/posts'), ler('mural/comentarios'), ler('perfis'), ler('pedidos')]);
  const desde = Math.max(ultimo, agora - 6 * 3600e3);
  const nome = (uid, fb) => (((perfis[uid] && perfis[uid].nome) || fb || 'Alguém').trim().split(/\s+/)[0]);
  const corta = (t, n) => { t = String(t || '').replace(/\s+/g, ' ').trim(); return t.length > n ? t.slice(0, n - 1) + '…' : t; };
  const fila = new Map();
  const add = (uid, autor, m) => { if(!uid || uid === autor) return; const l = fila.get(uid) || []; if(l.some(x => x.chave === m.chave)) return; l.push(m); fila.set(uid, l); };
  for(const [pid, p] of Object.entries(posts)){
    if(!p || !p.texto) continue;
    const tit = corta(p.titulo || p.texto, 60), link = BASE + '#mural-' + pid, tag = 'mural-' + pid;
    if(p.em > desde && p.em <= agora) for(const u of (p.men || [])) add(u, p.uid, {chave: 'p' + pid, titulo: `${nome(p.uid, p.nome)} marcou você no mural`, corpo: `“${tit}”: ${corta(p.texto, 90)}`, link, tag});
    const rs = Object.entries(com[pid] || {}).filter(([, c]) => c && c.texto).sort((a, b) => a[1].em - b[1].em);
    const ml = p.melhor, mc = ml && (com[pid] || {})[ml.c];
    if(mc && ml.em > desde && ml.em <= agora) add(mc.uid, p.uid, {chave: 'm' + pid + ml.c, titulo: `${nome(p.uid, p.nome)} escolheu a sua resposta como a melhor`, corpo: `“${tit}”: ${corta(mc.texto, 90)}`, link, tag});
    const participantes = new Set();
    for(const [cid, c] of rs){
      if(c.em > desde && c.em <= agora){
        const quem = nome(c.uid, c.nome), corpo = `“${tit}”: ${corta(c.texto, 90)}`, chave = 'c' + cid;
        for(const u of (c.men || [])) add(u, c.uid, {chave, titulo: `${quem} marcou você no mural`, corpo, link, tag});
        add(p.uid, c.uid, {chave, titulo: `${quem} respondeu ao seu tópico`, corpo, link, tag});
        for(const u of participantes) add(u, c.uid, {chave, titulo: `${quem} também respondeu`, corpo, link, tag});
      }
      participantes.add(c.uid);
    }
  }
  let n = 0;
  for(const [uid, msgs] of fila){
    const pu = pe[uid] && pe[uid].push; if(!pu || !pu.token || pu.mural === false) continue;
    const lista = [{uid, token: pu.token}];
    if(msgs.length > 3) await enviar(lista, `Psiu! ${msgs.length} novidades no mural`, msgs.slice(-3).map(m => m.titulo).join(' · '), BASE + '#mural', 'mural');
    else for(const m of msgs) await enviar(lista, m.titulo, m.corpo, m.link, m.tag);
    n += msgs.length;
  }
  await marco.set(agora);
  console.log(`::notice::Mural: ${n} notificações para ${fila.size} pessoas.`);
} else {
  await lembretes();
}
process.exit(0);
