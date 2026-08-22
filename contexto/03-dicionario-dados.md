# Dicionário de dados

Documentação das três tabelas fornecidas em [`../dados/`](../dados/), mantida
pelo time de engenharia de dados.

Os arquivos correspondem à **camada bruta**: o destino acumula as transmissões
recebidas do e-SUS PEC (uma carga completa seguida de cargas incrementais
mensais). A coluna `data_transmissao` indica em qual transmissão a linha chegou.

---

## Convenção de nomes

Os nomes de coluna seguem a convenção do e-SUS PEC. O prefixo indica o tipo de
conteúdo:

| Prefixo | Significado | Exemplo |
|---|---|---|
| `co_` | código / identificador | `co_fat_cidadao_pec` |
| `no_` | nome | `no_cidadao`, `no_equipe` |
| `dt_` | data | `dt_registro` |
| `ds_` | descrição (texto livre ou domínio) | `ds_sexo`, `ds_proced` |
| `nu_` | número ou código externo | `nu_cns`, `nu_cbo` |
| `st_` | indicador booleano (`1` = sim, `0` = não) | `st_faleceu` |
| `qt_` | quantidade / valor medido | `qt_glicemia` |

## Siglas

| Sigla | O que é |
|---|---|
| **CNS** | Cartão Nacional de Saúde. Identificador do cidadão no SUS. |
| **CPF** | Cadastro de Pessoa Física. |
| **INE** | Identificador Nacional de Equipe. Código da equipe de saúde da família. É a chave estável da equipe; o nome é texto livre digitado no sistema. |
| **CBO** | Classificação Brasileira de Ocupações. Identifica a categoria do profissional. Ex.: `2251` é a família dos médicos clínicos, `2235` a dos enfermeiros. |
| **CIAP-2** | Classificação Internacional da Atenção Primária. Codifica condições de saúde na APS. Ex.: `K86` — hipertensão sem complicações. |
| **CID-10** | Classificação Internacional de Doenças. Ex.: `I10` — hipertensão essencial. |
| **SIGTAP** | Tabela de procedimentos do SUS. Codifica o que foi feito no atendimento. |
| **UBS** | Unidade Básica de Saúde. |

Nas colunas `nu_ciap` e `nu_cid`, um mesmo atendimento pode ter mais de um
código, separados por `|`.

---

## `cidadao_pec.csv`

Cadastro mestre de cidadãos acompanhados pela atenção primária. Uma linha por
cidadão.

| Coluna | Tipo |
|---|---|
| `co_fat_cidadao_pec` | bigint — chave primária |
| `no_cidadao` | varchar |
| `dt_registro_nascimento` | date |
| `ds_sexo` | varchar |
| `nu_cns` | varchar |
| `nu_cpf_cidadao` | varchar |
| `nu_telefone_celular` | varchar |
| `st_faleceu` | smallint |
| `dt_ultima_atualizacao_cidadao` | timestamp |
| `st_diabetes_diagnosticada` | smallint |
| `st_hipertensao_diagnosticada` | smallint |
| `nu_ine` | varchar |
| `no_equipe` | varchar |
| `data_ultimo_atend_individual` | date |
| `equipe_ine_atendimento` | varchar |
| `equipe_nome_atendimento` | varchar |
| `nu_atend_ubs_ultimos_12_meses` | bigint |
| `data_transmissao` | date |

Notas:

- `nu_ine` / `no_equipe`: equipe de **vínculo** do cidadão.
  `equipe_ine_atendimento` / `equipe_nome_atendimento`: equipe que realizou o
  **último atendimento**. Podem divergir.
- `st_hipertensao_diagnosticada` e `st_diabetes_diagnosticada` indicam condição
  diagnosticada **em atendimento por médico ou enfermeiro**.

---

## `atendimento_individual.csv`

Atendimentos individuais, classificados por linha de cuidado. Contém apenas
atendimentos realizados por **médicos e enfermeiros**.

Um mesmo atendimento é classificado em todas as linhas de cuidado às quais
pertence.

| Coluna | Tipo |
|---|---|
| `co_seq_fat_atd_ind` | bigint — chave primária |
| `co_fat_cidadao_pec` | bigint — FK para `cidadao_pec` |
| `atend_ind_classificacao` | varchar |
| `nu_ciap` | varchar |
| `no_ciap` | varchar |
| `nu_cid` | varchar |
| `no_cid` | varchar |
| `no_profissional` | varchar |
| `nu_cbo` | varchar |
| `no_cbo` | varchar |
| `ds_local_atendimento` | varchar |
| `nu_ine` | varchar |
| `no_equipe` | varchar |
| `dt_registro` | date |
| `data_transmissao` | date |
| `propriedades` | varchar — JSON |
| `versao` | varchar |

Notas:

- `atend_ind_classificacao` é a linha de cuidado do atendimento. Valores
  possíveis nesta base: `GERAL`, `HIPERTENSÃO`,
  `HIPERTENSÃO - CONDIÇÃO RESOLVIDA`, `DIABETES`.
- `dt_registro` é a data do atendimento.

---

## `procedimentos.csv`

Procedimentos, medições e exames, consolidados a partir de várias origens de
registro no PEC.

| Coluna | Tipo |
|---|---|
| `tabela` | varchar |
| `co_seq_fat_proced` | varchar — chave primária |
| `co_fat_cidadao_pec` | bigint — FK para `cidadao_pec` |
| `co_proced` | varchar |
| `ds_proced` | varchar |
| `nu_ine` | varchar |
| `no_equipe` | varchar |
| `no_profissional` | varchar |
| `nu_cbo` | varchar |
| `no_cbo` | varchar |
| `dt_registro` | date |
| `qt_afericao_pressao_arterial` | varchar |
| `qt_glicemia` | varchar |
| `data_transmissao` | date |
| `propriedades` | varchar — JSON |
| `versao` | varchar |

Notas:

- `tabela` indica a origem do registro: `ficha_proced`, `proced_atend_ind` ou
  `atividade_coletiva`. `co_seq_fat_proced` é um identificador composto —
  prefixo da origem + chave original.
- `ds_proced` tem dois valores possíveis nesta base:
  `AFERIÇÃO DE PRESSÃO ARTERIAL` e `MEDIÇÃO PESO E ALTURA`.
- `qt_afericao_pressao_arterial` traz o resultado da aferição, em JSON, com
  pressão sistólica e diastólica. `qt_glicemia` está reservada para uso futuro.
- `dt_registro` é a data de realização do procedimento.

---

## Códigos CBO presentes nesta base

| CBO | Descrição |
|---|---|
| `225125` | Médico clínico |
| `225142` | Médico da estratégia de saúde da família |
| `223505` | Enfermeiro |
| `223565` | Enfermeiro da estratégia de saúde da família |
| `223208` | Cirurgião dentista — clínico geral |
| `322205` | Técnico de enfermagem |
| `515105` | Agente comunitário de saúde |
