/* =====================================================================
   ARQUIVO VIVO · DADOS DO SITE
   ---------------------------------------------------------------------
   Este é o único arquivo que precisa mudar no dia a dia. A página
   (index.html) lê estas listas e monta tudo sozinha: home, Prazos,
   calendário, páginas das disciplinas, busca, Modo prova, etc.

   Regras gerais pra não quebrar o site:
   • Cada item fica entre { } e termina com vírgula.
   • Textos ficam entre aspas simples: 'assim'. Se o texto tiver um
     apóstrofo ('), troque as aspas por crase: `texto com 'aspas'`.
   • Datas sempre no formato 'AAAA-MM-DD' (ex.: '2026-11-24').
   • Nome de disciplina: use o nome que já aparece na lista DISC ou em
     DISC_ALIASES (lá no fim). Se usar um nome novo, acrescente-o em
     DISC_ALIASES, senão o item não aparece na página da disciplina.
   • Depois de salvar, o site atualiza em 1 a 10 minutos (cache do
     GitHub). Se não mudar, atualize a página.
   ===================================================================== */


/* ---------------------------------------------------------------------
   1. PRAZOS E TAREFAS
   Aparecem em: Prazos e Tarefas, calendário, "Próximo prazo" da home,
   páginas das disciplinas, Modo prova e arquivo da agenda do celular.
   Formato:
     {materia: 'Neuroanatomia', tarefa: 'Prova', prazo: '2026-11-24', added: '2026-10-27'},
   • prazo: data de entrega/prova. Vencidos vão sozinhos pro "cemitério".
   • added: dia em que você cadastrou (mostra o selo "New!" por 4 dias).
   • O Modo prova aparece 7 dias antes quando a tarefa tem "Prova",
     "Simulado", "Avaliação", "Teste", "N1" ou "N2" no nome.
   • Tarefa de várias matérias: use materia: 'Geral' e cite os nomes
     das disciplinas no texto da tarefa (o site reconhece).
   --------------------------------------------------------------------- */
const TASKS = [
  {materia: 'Bases Biológicas', tarefa: 'Pesquisar Divisão Celular: Mitose e Meiose (fases e principais características)', prazo: '2026-08-24', added: '2026-08-20'},
  {materia: 'Bases Biológicas', tarefa: 'Estudar sobre Gametogênese (Masculina / Feminina)', prazo: '2026-08-31', added: '2026-08-20'},
  {materia: 'Bases Biológicas', tarefa: 'Prova N1', prazo: '2026-09-14', added: '2026-09-06'},
  {materia: 'Psicologia da Aprendizagem', tarefa: 'Trabalho N1', prazo: '2026-09-09', added: '2026-09-06'},
  {materia: 'Neuroanatomia', tarefa: 'Trabalho N1', prazo: '2026-09-15', added: '2026-09-06'},
  {materia: 'Desenvolvimento Adulto e Idoso', tarefa: 'Prova N1', prazo: '2026-09-22', added: '2026-09-06'},
  {materia: 'Neuroanatomia', tarefa: 'Prova N1', prazo: '2026-09-22', added: '2026-09-06'},
  {materia: 'Psicologia da Aprendizagem', tarefa: 'Prova N1', prazo: '2026-09-23', added: '2026-08-27'},
  {materia: 'Psicologia Experimental', tarefa: 'Trabalho N1', prazo: '2026-09-23', added: '2026-09-06'},
  {materia: 'Psicologia Experimental', tarefa: 'Prova N1', prazo: '2026-09-23', added: '2026-09-06'},
  {materia: 'Desenvolvimento Adulto e Idoso', tarefa: 'Trabalho N1', prazo: '2026-10-20', added: '2026-09-06'},
  {materia: 'Geral', tarefa: 'Simulado no Canvas (Psicologia do Desenvolvimento Adulto e Idoso, Psicologia da Aprendizagem, Neuroanatomia e Bases Biológicas)', prazo: '2026-11-03', added: '2026-10-27'},
  {materia: 'Bases Biológicas', tarefa: 'Prova', prazo: '2026-11-16', added: '2026-10-27'},
  {materia: 'Desenvolvimento Adulto e Idoso', tarefa: 'Prova', prazo: '2026-11-17', added: '2026-10-27'},
  {materia: 'Neuroanatomia', tarefa: 'Prova', prazo: '2026-11-24', added: '2026-10-27'},
  {materia: 'Psicologia Experimental', tarefa: 'Prova', prazo: '2026-11-25', added: '2026-10-27'},
];


/* ---------------------------------------------------------------------
   2. ATUALIZAÇÕES (feed da home)
   Coloque a mais nova em primeiro. Mantenha no máximo 5 itens: ao
   adicionar uma, apague a última.
   Formato:
     {date: '2026-11-05', disc: 'Neuroanatomia', desc: 'Novos slides.', link: {drive:'02'}},
   link (opcional) — pra onde o item leva ao ser clicado:
     {drive:'02'}                          pasta da disciplina 02 no Drive
     {disc:'02'}                           página da disciplina 02
     {page:'viewPrazos', target:'calendario'}  uma página do site
     {page:'viewEstudar'}  {page:'viewFerramentas'}  {page:'viewApoio', target:'glossario'}
     {url:'https://...'}                   qualquer link externo
   --------------------------------------------------------------------- */
const UPDATES = [
  {date: '2026-10-30', disc: 'Geral', desc: 'Páginas por disciplina, busca no site, modo prova, progresso salvo no aparelho e prazos direto na agenda do celular.', link: {scroll:'disciplinas'}},
  {date: '2026-10-30', disc: 'Geral', desc: 'Calendário de prazos na página Prazos e Tarefas. E a antiga "Conteúdo de apoio" virou "Extras", com glossário das disciplinas e guia ABNT com gerador de referências.', link: {page:'viewPrazos', target:'calendario'}},
  {date: '2026-10-28', disc: 'Geral', desc: 'Nova página "Conteúdo de apoio" (hoje Extras): passo a passo pra montar gráficos no Excel e no Google Planilhas.', link: {page:'viewApoio', target:'graficos'}},
  {date: '2026-10-27', disc: 'Bases Biológicas', desc: 'Novos slides das últimas aulas.', link: {drive:'01'}},
  {date: '2026-09-22', disc: 'Geral', desc: 'Página nova "Resumos interativos": resumos em HTML pra você estudar e memorizar.', link: {page:'viewEstudar'}}
];


/* ---------------------------------------------------------------------
   3. DISCIPLINAS E PASTAS DO DRIVE
   1 = primeiro semestre, 2 = segundo semestre (o atual).
   As disciplinas do semestre 2 ganham página própria (#disc-01 etc.).
   Formato: {n:'07', name:'Nome da disciplina', url:'link da pasta no Drive'},
   --------------------------------------------------------------------- */
const DISC = {
  1: [
    {n:'01', name:'Estatística Aplicada à Psicologia', url:'https://drive.google.com/drive/folders/1kiPG5CsHaQoyuZJE5xRM2pBNUKdLSLux'},
    {n:'02', name:'Fenômenos e Processos Psicológicos Básicos', url:'https://drive.google.com/drive/folders/1VmaCFELi-RJfb3OqolN60dfzZtuv7yWz'},
    {n:'03', name:'Introdução à Psicologia', url:'https://drive.google.com/drive/folders/1ySZ8RMbnr7oI2xUlypekVrB_EzjONQZZ'},
    {n:'04', name:'Psicologia do Desenvolvimento: Infância e Adolescência', url:'https://drive.google.com/drive/folders/1DgQKq_NNPJKkNV5q9iTj4LWtT6vXJMRH'},
    {n:'05', name:'Psicologia e Artes', url:'https://drive.google.com/drive/folders/1dDbvtliXGNopD4z9O1GpJQOSyUMcAwn3'},
    {n:'06', name:'Filosofia', url:'https://drive.google.com/drive/folders/1IfblTgec1PL0lWiEE3M13Uiu6sDallsk'},
    {n:'07', name:'Outros', url:'https://drive.google.com/drive/folders/1WQyLzo-2sAC0de89p1Bi33fHTmJHG5QB'},
  ],
  2: [
    {n:'01', name:'Bases Biológicas', url:'https://drive.google.com/drive/folders/1T5BqXrKGFw5VIOx7K01GJJ6iAWehyb2i'},
    {n:'02', name:'Neuroanatomia Humana', url:'https://drive.google.com/drive/folders/1PX5WupRCrjxJeV-9WbquOqz-jLf5EkpI'},
    {n:'03', name:'Psicologia da Aprendizagem', url:'https://drive.google.com/drive/folders/1W7cbLxmskMxA0NVw2iS0k1yozZLWq5qg'},
    {n:'04', name:'Psicologia Experimental', url:'https://drive.google.com/drive/folders/1Ho4W47I5X5w5Jm5k7dyPUS3aH2lEa60J'},
    {n:'05', name:'Desenvolvimento Adulto e Idoso', url:'https://drive.google.com/drive/folders/1YTD1M9leyd9G4dF-WftSdJ9LMmjKIW_1'},
    {n:'06', name:'Projeto de Extensão', url:'https://drive.google.com/drive/folders/17moMotizBwZ9TQgY7rzz3-IKcAM1py7b'},
  ]
};


/* ---------------------------------------------------------------------
   4. RESUMOS INTERATIVOS
   Formato:
     {materia: 'Neuroanatomia', titulo: 'Título', subtitulo: 'opcional', desc: 'Descrição curta.', link: 'https://...'},
   --------------------------------------------------------------------- */
const STUDY = [
  {
    materia: 'Neuroanatomia',
    titulo: 'Telencéfalo & Diencéfalo',
    desc: 'Três formas de testar o que você sabe — não só reler. Localize estruturas no esquema, treine com flashcards nos dois sentidos, e feche com um simulado.',
    link: 'https://resumoneuro.netlify.app/'
  },
  {
    materia: 'Neuroanatomia',
    titulo: 'Lobo occipital',
    desc: 'A mesma cena, vista através de cada função visual, e o que acontece quando essa função para de funcionar.',
    link: 'https://trabalhoneuro.netlify.app/'
  },
  {
    materia: 'Neuroanatomia',
    titulo: 'Neuroanatomia',
    subtitulo: 'De forma rápida e prática',
    desc: 'Um material interativo para revisar os principais conteúdos de Neuroanatomia de forma objetiva, com recursos pensados para facilitar a retomada e a fixação do conteúdo.',
    link: 'https://neuroanatomia.netlify.app/'
  },
  {
    materia: 'Psicologia da Aprendizagem',
    titulo: 'Teorias de aprendizagem: do Behaviorismo ao Humanismo',
    desc: 'Leia a teoria, depois force o cérebro a buscar a resposta sozinho. É esse esforço de buscar, e não reler, que fixa o conteúdo.',
    link: 'https://resumoaprendizagem.netlify.app/'
  },
  {
    materia: 'Psicologia da Aprendizagem',
    titulo: 'Psicologia da Aprendizagem',
    subtitulo: 'Testes rápidos e práticos',
    desc: 'Uma ferramenta para revisar os conteúdos da disciplina por meio de testes rápidos, ajudando a recuperar as informações da memória e identificar o que ainda precisa ser revisado.',
    link: 'https://psiaprendizagem.netlify.app/'
  },
  {
    materia: 'Psicologia Experimental',
    titulo: 'Teoria organizada para a prova',
    desc: 'Leia o tópico, responda o Teste-se de cabeça e, no fim, revise com os cartões.',
    link: 'https://resumoexperimental.netlify.app/'
  },
  {
    materia: 'Psicologia Experimental',
    titulo: 'Psicologia Experimental',
    subtitulo: 'Testes para treinar e fixar conteúdo',
    desc: 'Material de revisão com testes para praticar os conceitos da disciplina, conferir as respostas e reforçar os conteúdos estudados antes das avaliações.',
    link: 'https://psiexperimental.netlify.app/'
  }
];


/* ---------------------------------------------------------------------
   5. VÍDEOS DE APOIO (por número da disciplina do 2º semestre)
   Formato dentro dos colchetes da disciplina:
     {titulo: 'Nome do vídeo', youtubeId: 'código'}
   O código é o que vem depois de "v=" no link do YouTube
   (youtube.com/watch?v=ESTE_CODIGO) ou depois de "youtu.be/".
   --------------------------------------------------------------------- */
const VIDEOS = {
  '01': [{titulo:'O que é genética comportamental?', youtubeId:'5OaRKEhwnsc'}, {titulo:'Gametogênese', youtubeId:'04l1AdA_Sb4'}],
  '02': [{titulo:'Resumão Sistema Nervoso Central', youtubeId:'KBaRemG4_s0'}],
  '03': [{titulo:'Teorias da aprendizagem e do desenvolvimento', youtubeId:'JBcjnLDtRYs'}],
  '04': [],
  '05': [{titulo:'Desenvolvimento Humano: A adultez', youtubeId:'4RaUKkN-cvk'}],
  '06': []
};


/* ---------------------------------------------------------------------
   6. CURSOS EXTRAS
   Formato: {nome: 'Nome do curso', link: 'https://...', nota: 'Gratuito e com certificado', added: '2026-11-01'},
   --------------------------------------------------------------------- */
const COURSES = [
  {nome: 'Introdução à Epistemologia Genética de Jean Piaget (Edição 2026)', link: 'https://lumina.ufrgs.br/course/view.php?id=605', nota: 'Com certificado', added: '2026-08-20'},
  {nome: 'Saúde mental na escola', link: 'https://lumina.ufrgs.br/course/view.php?id=570', nota: 'Gratuito e com certificado', added: '2026-08-20'},
  {nome: 'Saúde mental, Direitos Humanos e Sistema Penal', link: 'https://lumina.ufrgs.br/course/view.php?id=571', nota: 'Gratuito e com certificado', added: '2026-08-20'},
];


/* ---------------------------------------------------------------------
   7. GLOSSÁRIO (página Extras, busca e páginas das disciplinas)
   Formato: {t: 'Termo', disc: 'Neuroanatomia', d: 'Definição curta.'},
   --------------------------------------------------------------------- */
const GLOSSARIO = [
  // Psicologia da Aprendizagem
  {t:'Condicionamento clássico (respondente)', disc:'Psicologia da Aprendizagem', d:'Aprendizagem em que um estímulo neutro, ao ser pareado repetidamente com um estímulo incondicionado, passa a eliciar uma resposta parecida com a resposta reflexa. Estudado por Pavlov.'},
  {t:'Estímulo incondicionado (EI)', disc:'Psicologia da Aprendizagem', d:'Estímulo que provoca uma resposta sem aprendizagem prévia. Ex.: comida na boca do cão de Pavlov.'},
  {t:'Resposta incondicionada (RI)', disc:'Psicologia da Aprendizagem', d:'Resposta reflexa, não aprendida, provocada pelo estímulo incondicionado. Ex.: salivar diante da comida.'},
  {t:'Estímulo neutro (EN)', disc:'Psicologia da Aprendizagem', d:'Estímulo que, antes do condicionamento, não provoca a resposta estudada. Ex.: o som da sineta antes dos pareamentos.'},
  {t:'Estímulo condicionado (EC)', disc:'Psicologia da Aprendizagem', d:'Estímulo antes neutro que, depois de pareado com o EI, passa a provocar a resposta. Ex.: a sineta após o condicionamento.'},
  {t:'Resposta condicionada (RC)', disc:'Psicologia da Aprendizagem', d:'Resposta aprendida, provocada pelo estímulo condicionado. Ex.: salivar ao ouvir a sineta.'},
  {t:'Condicionamento operante', disc:'Psicologia da Aprendizagem', d:'Aprendizagem em que a probabilidade de um comportamento muda de acordo com as consequências que ele produz. Estudado por Skinner.'},
  {t:'Reforço positivo', disc:'Psicologia da Aprendizagem', d:'Adicionar um estímulo após o comportamento, aumentando a chance de ele se repetir. Ex.: elogio depois de estudar.'},
  {t:'Reforço negativo', disc:'Psicologia da Aprendizagem', d:'Remover um estímulo aversivo após o comportamento, aumentando a chance de ele se repetir. Ex.: tomar remédio e a dor passar. Não é punição.'},
  {t:'Punição positiva', disc:'Psicologia da Aprendizagem', d:'Adicionar um estímulo aversivo após o comportamento, diminuindo a chance de ele se repetir. Ex.: levar bronca.'},
  {t:'Punição negativa', disc:'Psicologia da Aprendizagem', d:'Remover um estímulo agradável após o comportamento, diminuindo a chance de ele se repetir. Ex.: perder o videogame.'},
  {t:'Extinção', disc:'Psicologia da Aprendizagem', d:'Enfraquecimento de uma resposta quando ela deixa de ser reforçada (operante) ou quando o EC deixa de ser seguido pelo EI (respondente).'},
  {t:'Recuperação espontânea', disc:'Psicologia da Aprendizagem', d:'Reaparecimento de uma resposta já extinta depois de um intervalo de tempo sem exposição ao estímulo.'},
  {t:'Generalização', disc:'Psicologia da Aprendizagem', d:'Tendência de responder também a estímulos parecidos com o estímulo original. Ex.: o Pequeno Albert passando a temer outros objetos peludos.'},
  {t:'Discriminação', disc:'Psicologia da Aprendizagem', d:'Capacidade de responder a um estímulo específico e não a outros parecidos com ele.'},
  {t:'Modelagem', disc:'Psicologia da Aprendizagem', d:'Ensino de um comportamento novo reforçando aproximações sucessivas, cada vez mais próximas do comportamento final.'},
  {t:'Esquemas de reforçamento', disc:'Psicologia da Aprendizagem', d:'Regras que definem quando o reforço é liberado: contínuo (toda resposta) ou intermitente (razão fixa, razão variável, intervalo fixo, intervalo variável).'},
  {t:'Lei do efeito', disc:'Psicologia da Aprendizagem', d:'Princípio de Thorndike: respostas seguidas de consequências satisfatórias tendem a se fortalecer; as seguidas de desconforto tendem a enfraquecer.'},
  {t:'Aprendizagem por contiguidade', disc:'Psicologia da Aprendizagem', d:'Proposta de Guthrie: uma combinação de estímulos que acompanha um movimento tende a ser seguida por esse movimento quando se repete. A associação pode se formar em uma única tentativa.'},
  {t:'Redução do impulso (drive)', disc:'Psicologia da Aprendizagem', d:'Ideia central de Hull: o comportamento é motivado por necessidades biológicas, e respostas que reduzem esse impulso são reforçadas.'},
  {t:'Behaviorismo metodológico', disc:'Psicologia da Aprendizagem', d:'Posição de Watson (1913): a psicologia deve estudar apenas o comportamento observável, deixando de lado a introspecção.'},
  {t:'Aprendizagem observacional', disc:'Psicologia da Aprendizagem', d:'Aprender observando o comportamento de outras pessoas e suas consequências (modelação). Estudada por Bandura, como no experimento do boneco João Bobo.'},

  // Psicologia Experimental
  {t:'Variável independente (VI)', disc:'Psicologia Experimental', d:'Variável que o pesquisador manipula para ver o efeito. Ex.: tipo de técnica de estudo.'},
  {t:'Variável dependente (VD)', disc:'Psicologia Experimental', d:'Variável medida, que pode mudar em função da VI. Ex.: nota na prova.'},
  {t:'Variável estranha (interveniente)', disc:'Psicologia Experimental', d:'Fator que não é o foco do estudo, mas pode afetar a VD e precisa ser controlado. Ex.: horas de sono dos participantes.'},
  {t:'Grupo experimental', disc:'Psicologia Experimental', d:'Grupo que recebe a manipulação da variável independente.'},
  {t:'Grupo controle', disc:'Psicologia Experimental', d:'Grupo que não recebe a manipulação (ou recebe placebo) e serve de comparação.'},
  {t:'Hipótese', disc:'Psicologia Experimental', d:'Afirmação testável sobre a relação esperada entre variáveis, formulada antes da coleta de dados.'},
  {t:'População e amostra', disc:'Psicologia Experimental', d:'População é o conjunto total que se quer estudar; amostra é a parte dela que efetivamente participa da pesquisa.'},
  {t:'Distribuição aleatória', disc:'Psicologia Experimental', d:'Sortear os participantes entre os grupos, para que diferenças individuais se distribuam por igual e não expliquem o resultado.'},
  {t:'Linha de base', disc:'Psicologia Experimental', d:'Medida do comportamento antes da intervenção, usada como ponto de comparação. Muito usada na Análise do Comportamento.'},
  {t:'Delineamento de sujeito único (A-B-A)', disc:'Psicologia Experimental', d:'Delineamento em que o mesmo participante passa por linha de base (A), intervenção (B) e retirada da intervenção (A), servindo de controle para si mesmo.'},
  {t:'Duplo-cego', disc:'Psicologia Experimental', d:'Procedimento em que nem os participantes nem quem coleta os dados sabem quem está em cada grupo, para evitar vieses de expectativa.'},
  {t:'Validade interna', disc:'Psicologia Experimental', d:'Grau de confiança de que a mudança na VD foi causada pela VI, e não por variáveis estranhas.'},
  {t:'Validade externa', disc:'Psicologia Experimental', d:'Grau em que os resultados podem ser generalizados para outras pessoas, contextos e situações.'},
  {t:'Correlação', disc:'Psicologia Experimental', d:'Medida de quanto duas variáveis variam juntas. Correlação não prova causalidade: só o experimento controlado permite afirmar causa e efeito.'},
  {t:'Análise do Comportamento', disc:'Psicologia Experimental', d:'Abordagem baseada no behaviorismo radical de Skinner, que estuda as relações entre o comportamento e o ambiente (antecedentes e consequências).'},

  // Neuroanatomia
  {t:'Telencéfalo', disc:'Neuroanatomia', d:'Maior parte do encéfalo: os dois hemisférios cerebrais, com o córtex, os núcleos da base e estruturas como o hipocampo e a amígdala.'},
  {t:'Diencéfalo', disc:'Neuroanatomia', d:'Região central do encéfalo, entre o telencéfalo e o tronco encefálico. Inclui o tálamo e o hipotálamo.'},
  {t:'Tálamo', disc:'Neuroanatomia', d:'Estação de retransmissão: recebe e encaminha ao córtex a maior parte das informações sensoriais (exceto o olfato).'},
  {t:'Hipotálamo', disc:'Neuroanatomia', d:'Regula a homeostase: fome, sede, temperatura, ciclo sono-vigília e o sistema endócrino, por meio da hipófise.'},
  {t:'Córtex pré-frontal', disc:'Neuroanatomia', d:'Parte anterior do lobo frontal, associada às funções executivas: planejamento, tomada de decisão, controle de impulsos e memória de trabalho.'},
  {t:'Lobo occipital', disc:'Neuroanatomia', d:'Lobo da parte posterior do cérebro, responsável principalmente pelo processamento visual.'},
  {t:'Lobo temporal', disc:'Neuroanatomia', d:'Lobo lateral, envolvido na audição, na compreensão da linguagem e na memória.'},
  {t:'Lobo parietal', disc:'Neuroanatomia', d:'Integra informações sensoriais do corpo (tato, dor, temperatura) e participa da percepção espacial.'},
  {t:'Hipocampo', disc:'Neuroanatomia', d:'Estrutura do lobo temporal medial essencial para formar novas memórias declarativas e para a orientação espacial.'},
  {t:'Amígdala', disc:'Neuroanatomia', d:'Conjunto de núcleos do lobo temporal ligado ao processamento das emoções, especialmente o medo.'},
  {t:'Cerebelo', disc:'Neuroanatomia', d:'Estrutura na parte posterior e inferior do encéfalo, responsável pela coordenação dos movimentos, pelo equilíbrio e pela aprendizagem motora.'},
  {t:'Núcleos (gânglios) da base', disc:'Neuroanatomia', d:'Núcleos profundos que participam do controle dos movimentos voluntários. Sua disfunção está associada à doença de Parkinson.'},
  {t:'Tronco encefálico', disc:'Neuroanatomia', d:'Formado por mesencéfalo, ponte e bulbo. Controla funções vitais, como respiração e batimentos cardíacos.'},
  {t:'Área de Broca', disc:'Neuroanatomia', d:'Região do lobo frontal, em geral no hemisfério esquerdo, ligada à produção da fala.'},
  {t:'Área de Wernicke', disc:'Neuroanatomia', d:'Região do lobo temporal, em geral no hemisfério esquerdo, ligada à compreensão da linguagem.'},
  {t:'Corpo caloso', disc:'Neuroanatomia', d:'Feixe de fibras que conecta os dois hemisférios cerebrais e permite a comunicação entre eles.'},

  // Bases Biológicas
  {t:'Neurônio', disc:'Bases Biológicas', d:'Célula do sistema nervoso especializada em transmitir sinais. Partes: dendritos (recebem), corpo celular e axônio (conduz o impulso).'},
  {t:'Sinapse', disc:'Bases Biológicas', d:'Ponto de comunicação entre dois neurônios (ou entre neurônio e músculo), em geral pela liberação de neurotransmissores.'},
  {t:'Neurotransmissor', disc:'Bases Biológicas', d:'Substância química liberada na sinapse que transmite o sinal ao neurônio seguinte. Ex.: dopamina, serotonina, acetilcolina.'},
  {t:'Sistema nervoso simpático', disc:'Bases Biológicas', d:'Ramo do sistema nervoso autônomo que prepara o corpo para ação (luta ou fuga): acelera o coração, dilata as pupilas, reduz a digestão.'},
  {t:'Sistema nervoso parassimpático', disc:'Bases Biológicas', d:'Ramo do sistema nervoso autônomo que favorece repouso e recuperação: desacelera o coração e estimula a digestão.'},
  {t:'Mitose', disc:'Bases Biológicas', d:'Divisão celular que gera duas células-filhas geneticamente iguais à célula-mãe, com o mesmo número de cromossomos. Serve ao crescimento e à reparação.'},
  {t:'Meiose', disc:'Bases Biológicas', d:'Divisão celular que gera quatro células com metade dos cromossomos e variabilidade genética. Origina os gametas.'},
  {t:'Gametogênese', disc:'Bases Biológicas', d:'Formação dos gametas: espermatogênese (espermatozoides, nos testículos) e ovogênese (óvulos, nos ovários).'},
  {t:'Genótipo e fenótipo', disc:'Bases Biológicas', d:'Genótipo é o conjunto de genes de um indivíduo; fenótipo é o que se manifesta (características observáveis), resultado da interação entre genes e ambiente.'},
  {t:'Herdabilidade', disc:'Bases Biológicas', d:'Proporção da variação de uma característica numa população que pode ser atribuída a diferenças genéticas. Não diz o quanto de uma pessoa é "genético".'},
  {t:'Genética comportamental', disc:'Bases Biológicas', d:'Campo que estuda como fatores genéticos e ambientais influenciam diferenças de comportamento, por exemplo com estudos de gêmeos e de adoção.'},

  // Desenvolvimento Adulto e Idoso
  {t:'Intimidade x isolamento', disc:'Desenvolvimento Adulto e Idoso', d:'Estágio de Erikson do início da vida adulta: o desafio é construir vínculos próximos e duradouros sem perder a própria identidade.'},
  {t:'Generatividade x estagnação', disc:'Desenvolvimento Adulto e Idoso', d:'Estágio de Erikson da meia-idade: o desafio é contribuir para as próximas gerações (filhos, trabalho, comunidade).'},
  {t:'Integridade x desespero', disc:'Desenvolvimento Adulto e Idoso', d:'Estágio de Erikson da velhice: o desafio é olhar para a própria vida e aceitá-la como teve sentido.'},
  {t:'Senescência', disc:'Desenvolvimento Adulto e Idoso', d:'Envelhecimento natural e gradual do organismo, que acontece com todos, sem ser doença.'},
  {t:'Senilidade', disc:'Desenvolvimento Adulto e Idoso', d:'Alterações no envelhecimento causadas por doenças ou condições patológicas, e não pelo processo natural.'},
  {t:'Inteligência fluida', disc:'Desenvolvimento Adulto e Idoso', d:'Capacidade de raciocinar e resolver problemas novos. Tende a declinar gradualmente com a idade.'},
  {t:'Inteligência cristalizada', disc:'Desenvolvimento Adulto e Idoso', d:'Conhecimentos e habilidades acumulados pela experiência, como vocabulário. Tende a se manter ou crescer na vida adulta.'},
  {t:'Plasticidade', disc:'Desenvolvimento Adulto e Idoso', d:'Capacidade do cérebro e do comportamento de se modificar com a experiência, que continua presente ao longo de toda a vida.'},
  {t:'Reserva cognitiva', disc:'Desenvolvimento Adulto e Idoso', d:'Capacidade do cérebro de compensar perdas; escolaridade e atividades estimulantes ao longo da vida estão associadas a uma reserva maior.'},

  // Geral / trabalhos acadêmicos
  {t:'Fichamento', disc:'Trabalhos acadêmicos', d:'Registro organizado das ideias principais de um texto, com a referência completa e, se houver citações diretas, as páginas.'},
  {t:'Resenha', disc:'Trabalhos acadêmicos', d:'Texto que resume uma obra e apresenta uma avaliação crítica dela.'},
  {t:'Paráfrase', disc:'Trabalhos acadêmicos', d:'Reescrever a ideia de um autor com as suas palavras, mantendo o sentido. Mesmo assim, precisa citar a fonte.'},
  {t:'Et al.', disc:'Trabalhos acadêmicos', d:'Expressão latina ("e outros") usada depois do sobrenome do primeiro autor quando a obra tem mais de três autores. Vai em itálico.'},
  {t:'Apud', disc:'Trabalhos acadêmicos', d:'Expressão latina ("citado por") usada na citação de citação, quando você não teve acesso ao texto original. Vai em itálico.'},
  {t:'Plágio', disc:'Trabalhos acadêmicos', d:'Apresentar ideias ou trechos de outra pessoa como se fossem seus, sem citar a fonte. Vale também para paráfrases sem referência.'},
];


/* ---------------------------------------------------------------------
   8. SIMULADOS (página oculta no momento)
   Formato: {titulo: 'Nome', url: 'https://...', nota: 'opcional'}
   --------------------------------------------------------------------- */
const SIMULADOS = {
  '01': [{titulo:'Simulado: Processos Biológicos', url:'https://wayground.com/join?gc=54972837', nota:'Código de sessão do Wayground'}],
  '02': [{titulo:'Simulado: Neuroanatomia', url:'https://wayground.com/join?gc=36380213', nota:'Código de sessão do Wayground'}],
  '03': [{titulo:'Simulado: Psicologia da Aprendizagem', url:'https://wayground.com/join?gc=05231629', nota:'Código de sessão do Wayground'}],
  '04': [{titulo:'Simulado: Psicologia Experimental', url:'https://wayground.com/join?gc=18994189', nota:'Código de sessão do Wayground'}],
  '05': [{titulo:'Simulado: Desenvolvimento Adulto e Idoso', url:'https://wayground.com/join?gc=62884597', nota:'Código de sessão do Wayground'}],
  '06': []
};


/* ---------------------------------------------------------------------
   9. NOMES ALTERNATIVOS DAS DISCIPLINAS
   Liga os nomes usados nas listas acima à disciplina certa.
   Ex.: 'Neuroanatomia' e 'Neuroanatomia Humana' são a disciplina 02.
   --------------------------------------------------------------------- */
const DISC_ALIASES = {
  '01': ['Bases Biológicas'],
  '02': ['Neuroanatomia Humana', 'Neuroanatomia'],
  '03': ['Psicologia da Aprendizagem'],
  '04': ['Psicologia Experimental'],
  '05': ['Desenvolvimento Adulto e Idoso', 'Psicologia do Desenvolvimento Adulto e Idoso'],
  '06': ['Projeto de Extensão', 'Extensão'],
};
