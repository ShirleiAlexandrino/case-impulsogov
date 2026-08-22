# Regras de negócio: acompanhamento da pessoa com hipertensão

Versão simplificada das regras do Ministério da Saúde (Nota Metodológica C5 —
Cuidado da pessoa com hipertensão). O que está aqui é suficiente para construir
a modelagem; não é necessário consultar a nota original.

## Data de referência

Os dados fornecidos são um **retrato extraído em 2026-08-01**. Todas as janelas
de tempo devem ser calculadas em relação a essa data, e não à data em que você
estiver executando o código.

## 1. Quem entra na lista

**Critério de entrada.** É considerada pessoa com hipertensão quem teve, em
algum momento do histórico, um **atendimento individual com hipertensão como
condição avaliada**, realizado por **médico ou enfermeiro**.

Não há janela de tempo para a entrada: um diagnóstico registrado em 2015 vale
hoje. Hipertensão é condição crônica.

**Códigos que caracterizam hipertensão** (já aplicados na coluna
`atend_ind_classificacao` da tabela de atendimentos):

- CIAP-2: `K86`, `K87`
- CID-10: `I10`, `I11*`, `I12*`, `I13*`, `I15*`, `O10*`, `O11`

**Critérios de saída.** Sai da lista quem:

- **faleceu**; ou
- teve a **condição registrada como resolvida**. No PEC, o profissional pode
  marcar uma condição como resolvida — na tabela de atendimentos isso aparece
  como a classificação `HIPERTENSÃO - CONDIÇÃO RESOLVIDA`.



## 2. As boas práticas de acompanhamento

Para cada pessoa da lista, avaliam-se três boas práticas.

| Boa prática | Janela | Profissionais que contam (família CBO) |
|---|---|---|
| **Consulta** — ao menos um atendimento individual nos últimos 6 meses, em qualquer local | últimos **6 meses** | médicos (`2231`, `2251`, `2252`, `2253`) e enfermeiros (`2235`) |
| **Aferição de pressão arterial** — ao menos um registro nos últimos 6 meses | últimos **6 meses** | médicos, enfermeiros e técnicos/auxiliares de enfermagem (`3222`) |
| **Registro simultâneo de peso e altura** nos últimos 12 meses | últimos **12 meses** | médicos, enfermeiros, técnicos de enfermagem (`3222`) e agentes comunitários de saúde (`5151`) |

Notas:

- O registro de **peso e altura** só conta quando as duas medidas foram feitas
  no mesmo dia. 
- Contam registros feitos por **qualquer profissional habilitado da APS**, não
  apenas pela equipe à qual a pessoa está vinculada.

## 3. Os três status exibidos

Para cada boa prática, a tela mostra um dos três status:

| Status | Definição |
|---|---|
| **Em dia** | O registro mais recente está dentro da janela. |
| **Atrasada** | Existe registro, mas o mais recente está fora da janela. |
| **Nunca realizada** | Não existe nenhum registro dessa boa prática no histórico da pessoa. |

