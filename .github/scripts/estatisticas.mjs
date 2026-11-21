// Números gerais da turma (sem nomes) para o painel do administrador.
// Lê o progresso salvo de cada conta e grava só médias e contagens em pedidos/_estatisticas,
// que só o administrador consegue ler. Grupos com menos de 3 pessoas não entram.
import admin from 'firebase-admin';

const SA = process.env.FIREBASE_SERVICE_ACCOUNT;
if(!SA){ console.log('Segredo FIREBASE_SERVICE_ACCOUNT não configurado.'); process.exit(0); }
admin.initializeApp({ credential: admin.credential.cert(JSON.parse(SA)), databaseURL: 'https://arquivo-vivo-psi-default-rtdb.firebaseio.com' });
const db = admin.database();
const MIN = 3;
const isoBR = ms => new Date(ms - 3 * 3600e3).toISOString().slice(0, 10);
const hoje = isoBR(Date.now());
const diasAtras = n => isoBR(Date.now() - n * 864e5);
const json = (v, padrao) => { try{ return v ? JSON.parse(v) : padrao; }catch(_){ return padrao; } };
const sim = v => v === true || v === 'true' || v === 1;

const [us, ac, ap] = await Promise.all(['usuarios', 'acesso', 'apoiadores'].map(async k => (await db.ref(k).get()).val() || {}));

const porDia = {};                 // data -> Set de contas
const simAgg = {};                 // simulado -> {pessoas:Set, somaPct, n}
const temaAgg = {};                // sim|tema -> {a, n, pessoas:Set}
const psiu = {};                   // pergunta normalizada -> {t, pessoas:Set, sem:Set}
let dsResp = 0; const dsPessoas = new Set();
let comProgresso = 0;

const norm = t => String(t).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9 ]/g, ' ').replace(/\s+/g, ' ').trim();

for(const [uid, u] of Object.entries(us)){
  const pr = (u && u.progresso) || {}; const L = {};
  for(const [k, v] of Object.entries(pr)) L[decodeURIComponent(k)] = v;
  if(Object.keys(L).length) comProgresso++;
  const marca = d => { if(d && d >= diasAtras(13)) (porDia[d] = porDia[d] || new Set()).add(uid); };
  const tempo = json(L['av-tempo'], {});
  for(const [d, seg] of Object.entries(tempo.dias || {})) if(seg >= 60) marca(d);
  const de = json(L['av-desempenho'], {sims:{}, hist:[]});
  for(const h of de.hist || []){ if(h.t) marca(isoBR(h.t)); }
  // simulados: média da melhor tentativa de cada pessoa
  const melhor = {};
  for(const h of de.hist || []) if(h.id && typeof h.pct === 'number') melhor[h.id] = Math.max(melhor[h.id] ?? 0, h.pct);
  for(const [id, pct] of Object.entries(melhor)){ const a = simAgg[id] = simAgg[id] || {pessoas:new Set(), soma:0}; a.pessoas.add(uid); a.soma += pct; }
  for(const [id, temas] of Object.entries(de.sims || {})) for(const [tema, x] of Object.entries(temas || {})){
    const a = temaAgg[id + '|' + tema] = temaAgg[id + '|' + tema] || {a:0, n:0, pessoas:new Set()}; a.a += x.a || 0; a.n += x.n || 0; a.pessoas.add(uid); }
  const ds = json(L['av-discursiva'], {});
  for(const h of ds.hist || []){ dsResp += h.n || 0; dsPessoas.add(uid); if(h.t) marca(isoBR(h.t)); }
  for(const p of json(L['av-psiu-perguntas'], [])){
    const k = norm(p.t); if(k.length < 3) continue;
    const a = psiu[k] = psiu[k] || {t: p.t, pessoas:new Set(), sem:new Set()}; a.pessoas.add(uid); if(p.s) a.sem.add(uid);
    if(p.em) marca(isoBR(p.em));
  }
}

const dias = []; for(let i = 13; i >= 0; i--){ const d = diasAtras(i); dias.push({d, n: porDia[d] ? porDia[d].size : 0}); }
const contaDias = n => { const s = new Set(); for(let i = 0; i < n; i++){ const d = diasAtras(i); if(porDia[d]) porDia[d].forEach(x => s.add(x)); } return s.size; };
const saida = {
  em: Date.now(),
  contas: { liberadas: Object.values(ac).filter(sim).length, apoiadores: Object.values(ap).filter(sim).length, comProgresso },
  ativos: { d1: contaDias(2), d7: contaDias(7) },
  dias,
  simulados: Object.entries(simAgg).filter(([, a]) => a.pessoas.size >= MIN).map(([id, a]) => ({id, pessoas: a.pessoas.size, media: Math.round(a.soma / a.pessoas.size)})).sort((x, y) => x.media - y.media),
  temas: Object.entries(temaAgg).filter(([, a]) => a.pessoas.size >= MIN && a.n >= 10).map(([k, a]) => ({sim: k.split('|')[0], tema: k.split('|').slice(1).join('|'), pct: Math.round(a.a / a.n * 100), pessoas: a.pessoas.size})).sort((x, y) => x.pct - y.pct).slice(0, 10),
  discursiva: { respostas: dsResp, pessoas: dsPessoas.size },
  psiu: {
    top: Object.values(psiu).filter(a => a.pessoas.size >= 2).sort((x, y) => y.pessoas.size - x.pessoas.size).slice(0, 12).map(a => ({t: a.t, n: a.pessoas.size})),
    sem: Object.values(psiu).filter(a => a.sem.size >= 2).sort((x, y) => y.sem.size - x.sem.size).slice(0, 12).map(a => ({t: a.t, n: a.sem.size}))
  }
};
await db.ref('pedidos/_estatisticas').set(saida);
console.log(`::notice::Números da turma atualizados: ${saida.contas.liberadas} contas, ${saida.ativos.d7} ativas em 7 dias, ${saida.simulados.length} simulados com 3+ pessoas.`);
process.exit(0);
