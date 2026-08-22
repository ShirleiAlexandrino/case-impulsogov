# SQL da modelagem

**Dialeto: DuckDB.** Roda diretamente sobre os três CSVs em [`../dados/`](../dados/),
sem necessidade de outro banco.

Código completo, comentado por camada, em [`../sql/`](../sql/):

| Arquivo | Camada | O que faz |
|---|---|---|
| [`01_bronze.sql`](../sql/01_bronze.sql) | Bronze | Ingestão bruta dos três CSVs, com tipagem explícita (`VARCHAR`) nos campos que parecem numéricos mas são identificadores — evita que a auto-detecção de tipo corrompa zeros à esquerda ou quebre chaves compostas. |
| [`02_silver.sql`](../sql/02_silver.sql) | Silver | Deduplicação por chave (mantém a transmissão mais recente), extração dos campos que vêm dentro do JSON `propriedades`. |
| [`03_gold.sql`](../sql/03_gold.sql) | Gold | Critério de entrada/saída da lista e cálculo dos três status — é a tabela final, `gold_lista_nominal_hipertensao`. |
| [`04_metricas.sql`](../sql/04_metricas.sql) | — | As duas queries que produzem os números abaixo. |

Para como cada regra foi implementada e por quê, ver
[`01-diagrama-arquitetura.md`](01-diagrama-arquitetura.md).

## Os números

**325 pessoas** na Lista Nominal de Hipertensão, no retrato de 01/08/2026.

Distribuição de status por boa prática:

| Boa prática | Em dia | Atrasada | Nunca realizada |
|---|---|---|---|
| Consulta | 192 (59%) | 133 (41%) | 0 — impossível por definição, ver nota¹ |
| Aferição de pressão | 167 (51%) | 112 (34%) | 46 (14%) |
| Peso e altura | 135 (42%) | 116 (36%) | 74 (23%) |

¹ Entrar na lista já exige ter tido uma consulta com médico/enfermeiro — então
"Nunca realizada" nunca ocorre para Consulta, por construção da regra de
entrada, não por ausência de dado.

Reproduzível rodando [`01_bronze.sql`](../sql/01_bronze.sql) →
[`02_silver.sql`](../sql/02_silver.sql) → [`03_gold.sql`](../sql/03_gold.sql) →
[`04_metricas.sql`](../sql/04_metricas.sql), nessa ordem, num banco DuckDB.
