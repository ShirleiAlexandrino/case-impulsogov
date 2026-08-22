# Mensagem para o time de engenharia de dados

*Formato: Slack, canal do time responsável pela extração do e-SUS PEC.*

---

Fala, pessoal! 👋

Rodando a modelagem da Lista Nominal de Hipertensão em cima do que vocês
exportam do e-SUS PEC, encontrei alguns problemas nos dados. Priorizei os
**três** que eu resolveria primeiro:

**1. Falta o campo de microárea**
Nenhuma das três tabelas (`cidadao_pec`, `atendimento_individual`,
`procedimentos`) tem microárea — só equipe (`nu_ine`/`no_equipe`), que é um
nível acima. O protótipo da tela, já aprovado pelo produto, tem filtro por
microárea — então isso bloqueia uma funcionalidade que já foi validada. Sei
que o ACS registra microárea no e-SUS PEC — dá pra incluir na extração?

**2. O mesmo atendimento muda de valor entre cargas**
Peguei o atendimento `co_seq_fat_atd_ind = 4100004.HIPERTENSÃO` (cidadão
700001): chega em maio com `no_equipe = "ESF 2"`, e em junho o *mesmo*
registro histórico (mesma data, 2023-08-06) chega como `"Esf 2"`. Não é
isolado — vi vários assim. Se a carga é incremental, um fato histórico não
devia mudar de texto entre reenvios. É normalização sem controle de versão,
ou reprocessamento total a cada carga? Hoje dedupliquei por "fica a
transmissão mais recente" — queria confirmar se é mesmo a lógica certa.

**3. Dicionário de dados desatualizado**
Duas divergências entre o que está documentado e o que veio no CSV:
- `co_seq_fat_atd_ind` está documentado como `bigint`, mas os valores reais
  são compostos (ex. `"4100001.HIPERTENSÃO"` — id + linha de cuidado). Tive
  que tratar como texto.
- `atendimento_individual.csv` diz conter só atendimentos de médico/
  enfermeiro, mas tem registros com CBO de técnico de enfermagem (`322205`),
  classificação `GERAL`.

Vale atualizar a doc ou a extração, pra próxima pessoa não confiar no tipo ou
na regra errada.

**Outros achados, sem prioridade imediata:**
- **Dois `nu_ine` com o mesmo `no_equipe`.** `0001234571` e `0001234572`
  aparecem ambos gravados como `"ESF 5"` (169 e 165 cidadãos cada). Como
  `no_equipe` é texto livre e `nu_ine` é a chave estável, qualquer relatório
  agrupado pelo nome — em vez do código — mistura duas equipes reais numa só
  linha, sem erro visível. Achei isso construindo um controle de acesso por
  `nu_ine` — vale avisar o produto também.
- **Datas no futuro e nascimentos implausíveis.** Checagem automática contra
  a data do retrato (2026-08-01) achou 27 atendimentos e 19 procedimentos com
  `dt_registro` no futuro, e 5 nascimentos implausíveis — inclui o caso de
  idade 0 já citado antes. Sintoma de erro de captura na origem.
- `qt_afericao_pressao_arterial` e `qt_glicemia` existem como colunas mas
  vêm sempre vazias — o valor real está solto em JSON em `propriedades`. Dá
  pra estruturar?

Posso mandar as queries que usei pra achar cada um desses casos, se ajudar a
investigar. 🙏
