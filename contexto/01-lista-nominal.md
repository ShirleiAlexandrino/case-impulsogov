# Contexto: atenção primária, e-SUS PEC e listas nominais

Este documento dá o mínimo de contexto de domínio necessário para o case. Não é
preciso conhecimento prévio de saúde pública.

## Atenção Primária à Saúde (APS)

A APS é a porta de entrada do SUS. O território de um município é dividido entre
**equipes de saúde da família (eSF)**, e cada equipe é responsável por uma
população adscrita — as pessoas que moram na sua área. Uma equipe típica tem
médico, enfermeiro, técnicos de enfermagem e agentes comunitários de saúde (ACS).

Cada equipe é identificada por um **INE** (Identificador Nacional de Equipe),
um código numérico. O INE é a chave estável da equipe; o nome da equipe é texto
livre digitado no sistema.

A área de cada equipe é subdividida em **microáreas**, cada uma sob
responsabilidade de um ACS.

## e-SUS PEC

O **e-SUS APS PEC** é o prontuário eletrônico usado nas unidades básicas de
saúde. Cada cadastro, atendimento, procedimento e visita gera um registro. Esses registros
são exportados periodicamente para bases analíticas. Esses dados são inputados diretamente pelos profissionais de saúde durantes os processos e podem contem inconsistências e erros de registro.



## O que é uma lista nominal

Uma **lista nominal** é uma lista de pessoas, com nome e contato, que a equipe
de saúde usa para agir. Não é um relatório gerencial: é um instrumento de
trabalho da rotina da equipe.

O uso concreto é este: o enfermeiro abre a lista nominal de hipertensão da sua
equipe, filtra quem está com alguma boa prática atrasada, e a partir dela a
equipe orienta os ACS sobre quem
visitar naquela semana, liga para as pessoas, agenda consultas e outros.

Isso tem duas consequências para a modelagem:

- **A pessoa é a unidade da tabela.** Uma linha por cidadão.
- **Errar tem custo operacional.** Uma pessoa que aparece indevidamente na lista
  gera uma busca inútil. Uma pessoa que deveria aparecer e não aparece deixa
  de ser acompanhada. Um número agregado errado leva a equipe a priorizar a
  ação errada.

## O produto deste case

O protótipo em [prototipo-lista-nominal.png](prototipo-lista-nominal.png) é a
tela da Lista Nominal de Hipertensão. Ela mostra, por pessoa, a situação de cada
**boa prática** de acompanhamento — se está em dia, atrasada ou se nunca foi
realizada.

As regras que definem quem entra na lista e o que conta como boa prática estão
em [02-regras-hipertensao.md](02-regras-hipertensao.md).
