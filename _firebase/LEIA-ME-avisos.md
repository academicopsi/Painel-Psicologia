# Avisos no celular: disparo confiável

O GitHub atrasa muito os agendamentos de repositórios com pouco movimento (já houve atraso de 5 horas).
Por isso a tarefa "Mural (notificações)" é disparada de fora, a cada 5 minutos, pelo cron-job.org.

Cada disparo faz, nesta ordem:
1. Lembretes de provas e entregas do dia (uma vez por dia, entre 18h07 e 23h).
2. Avisos escritos no Painel do administrador.
3. Respostas, marcações e melhores respostas do mural.

Configuração no cron-job.org:
- URL: https://api.github.com/repos/academicopsi/Painel-Psicologia/actions/workflows/mural.yml/dispatches
- Agenda: a cada 5 minutos
- Método: POST
- Cabeçalhos: `Authorization: Bearer <token do GitHub>` e `Accept: application/vnd.github+json`
- Corpo: `{"ref":"main"}`
- Resposta esperada no teste: 204

O token é um "fine-grained token" do GitHub com acesso só a este repositório e permissão Actions: leitura e escrita.
Nunca colar o token no chat nem no código. Quando ele vencer, gerar outro e trocar no cron-job.org.
