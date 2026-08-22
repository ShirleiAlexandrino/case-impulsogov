# Aplicação de LGPD na Lista Nominal de Hipertensão

## Classificação do dado

A tabela `gold_lista_nominal_hipertensao` contém:

- **Dado pessoal sensível** (LGPD, art. 5º, II): condição de saúde
  (hipertensão) e histórico de acompanhamento clínico de cada pessoa.
- **Identificadores diretos**: nome, CPF, CNS, telefone celular.
- **Identificador indireto / pseudônimo interno**: `co_fat_cidadao_pec` — não
  identifica sozinho, mas combinado com as demais colunas, sim.

Dado de saúde tem tratamento mais restrito na LGPD (art. 11) do que dado
pessoal comum — por isso vale tratar essa tabela com cuidado redobrado, mesmo
sendo um case técnico com dado fictício.

## Base legal

O tratamento aqui serve ao acompanhamento clínico de pessoas com hipertensão
por uma equipe de saúde da família, dentro do SUS. Isso se enquadra em:

- **Art. 11, II, "f"** — tutela da saúde, exclusivamente em procedimento
  realizado por profissionais de saúde, serviços de saúde ou autoridade
  sanitária.
- **Art. 7º, III** (subsidiariamente) — execução de políticas públicas pela
  administração pública.

Isso justifica reunir nome, CPF/CNS, telefone e situação de saúde numa única
tela: sem esses dados juntos, a equipe não consegue localizar e agir sobre a
pessoa, que é o propósito declarado da lista nominal. Não seria uma
justificativa válida para reunir os mesmos dados num relatório de BI que não
precisa agir sobre indivíduos — daí a separação em camadas abaixo.

## O que foi aplicado (`sql/05_privacidade_lgpd.sql`)

Minimização de dados (art. 6º, III) por finalidade de acesso, em três
camadas:

| Camada | Finalidade | O que expõe |
|---|---|---|
| `gold_lista_nominal_hipertensao` | Ação operacional da equipe (ligar, agendar, visitar) | Identificação completa — é a única camada que precisa disso |
| `..._mascarado` | Suporte/QA — localizar um caso para investigar | Nome (conferência humana) + CPF/CNS mascarados; **sem telefone** |
| `..._analitico` | Gestão agregada, cobertura do programa | Nenhum identificador — só equipe, faixa etária e os três status |

O princípio: cada consumidor recebe o mínimo necessário para sua finalidade,
não o máximo disponível. A query de métricas do entregável 2
(`sql/04_metricas.sql`) já seguia essa lógica antes mesmo desta camada —
nunca usou nome, CPF, CNS ou telefone.

## Controle de acesso (atualização: implementado no app, não no banco)

Quando este documento foi escrito, "quem pode consultar cada view" estava
listado como fora do escopo — dependeria de papéis/roles no banco. Isso
mudou: o `app.py` (Streamlit) agora implementa controle de acesso por
perfil, usando `nu_ine` como identidade (não existe tabela de usuário/login
nos dados de origem, então `nu_ine` faz esse papel):

- **Perfil de equipe** — só acessa a Lista nominal e o Painel de cobertura
  da própria equipe (filtro por `nu_ine` aplicado assim que a pessoa entra).
- **Perfil de gestão** — acessa o Painel de cobertura de todas as equipes,
  mas **não tem acesso à Lista nominal identificada** (nome, CPF, CNS,
  telefone) de nenhuma equipe — só a `_analitico`, sem identificador.

Isso ainda é controle de acesso **na aplicação**, não no banco — as views
SQL (`gold_lista_nominal_hipertensao`, `..._mascarado`, `..._analitico`)
continuam sem RLS/roles própria; qualquer conexão direta ao banco ainda
enxerga tudo. Se este app for para produção com um SGBD real, vale
replicar essa mesma regra como papéis/roles no banco — hoje ela existe só
na camada Python.

## O que continua fora do escopo

- **Retenção e descarte**: por quanto tempo manter o histórico de uma pessoa
  após ela sair da lista (óbito, condição resolvida) é uma decisão de
  política de dados, não de SQL nem do app.
- **Log de acesso/auditoria** sobre quem consultou dado sensível de quem —
  o app não registra quem logou como qual equipe nem quando.
- **Canal para direitos do titular** (acesso, correção, exclusão) — depende
  de processo organizacional, não da tabela ou do app em si.

Esses três pontos ficam como recomendação para o time de dados e o
DPO/encarregado da organização — não são algo que uma modelagem SQL ou um
front-end resolvem sozinhos.
