# Mensagem para o time de engenharia de dados

*Formato: Slack, canal do time responsável pela extração do e-SUS PEC.*

---

Olá, pessoal!

Durante a modelagem da Lista Nominal de Hipertensão, a partir do que vocês
exportam do e-SUS PEC, encontrei alguns problemas nos dados. Priorizei os
**três** que eu resolveria primeiro:

**1. Falta o campo de microárea**
Nenhuma das três tabelas (`cidadao_pec`, `atendimento_individual`,
`procedimentos`) tem microárea — só equipe (`nu_ine`/`no_equipe`), que é um
nível acima. O protótipo da tela, já aprovado pelo produto, tem filtro por
microárea — então isso bloqueia uma funcionalidade que já foi validada. Sei
que o ACS registra microárea no e-SUS PEC — seria possível incluí-la na
extração?

**2. O mesmo atendimento muda de valor entre cargas**
Identifiquei o atendimento `co_seq_fat_atd_ind = 4100004.HIPERTENSÃO`
(cidadão 700001): chega em maio com `no_equipe = "ESF 2"`, e em junho o
*mesmo* registro histórico (mesma data, 2023-08-06) chega como `"Esf 2"`.
Não é um caso isolado — encontrei vários assim. Se a carga é incremental, um
fato histórico não deveria mudar de texto entre reenvios. É normalização sem
controle de versão, ou reprocessamento total a cada carga? Hoje dedupliquei
mantendo a transmissão mais recente — gostaria de confirmar se essa é
realmente a lógica correta.

**3. Dicionário de dados desatualizado**
Duas divergências entre o que está documentado e o que veio no CSV:
- `co_seq_fat_atd_ind` está documentado como `bigint`, mas os valores reais
  são compostos (ex. `"4100001.HIPERTENSÃO"` — id + linha de cuidado). Foi
  necessário tratá-lo como texto.
- `atendimento_individual.csv` diz conter só atendimentos de médico ou
  enfermeiro, mas tem registros com CBO de técnico de enfermagem (`322205`),
  classificação `GERAL`.

Recomendo atualizar a documentação ou a extração, para que a próxima pessoa
não confie no tipo ou na regra errada.

**Outros achados, sem prioridade imediata:**
- **Dois `nu_ine` com o mesmo `no_equipe`.** `0001234571` e `0001234572`
  aparecem ambos gravados como `"ESF 5"` (169 e 165 cidadãos, respectivamente).
  Como `no_equipe` é texto livre e `nu_ine` é a chave estável, qualquer
  relatório agrupado pelo nome — em vez do código — mistura duas equipes
  reais numa só linha, sem erro visível. Identifiquei isso ao construir um
  controle de acesso por `nu_ine` — vale avisar o time de produto também.
- **Datas no futuro e nascimentos implausíveis.** A checagem automática
  contra a data do retrato (2026-08-01) encontrou 27 atendimentos e 19
  procedimentos com `dt_registro` no futuro, além de 5 nascimentos
  implausíveis — incluindo o caso de idade 0 já citado. Parece sintoma de
  erro de captura na origem.
- `qt_afericao_pressao_arterial` e `qt_glicemia` existem como colunas, mas
  vêm sempre vazias — o valor real está em JSON, dentro de `propriedades`.
  Seria possível estruturar esse campo?

Posso compartilhar as queries que utilizei para identificar cada um desses
casos, caso ajude na investigação.
