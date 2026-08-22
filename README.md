# Case técnico — Analytics Engineer Sênior

Obrigado pelo interesse na vaga. Este case simula uma tarefa real do time:
transformar dados brutos da atenção primária em uma tabela que sustenta um
produto usado por equipes de saúde.

## Esforço e prazo

- **Esforço esperado: até 5 horas.** O case foi dimensionado para isso. Se você
  estiver passando muito disso, prefira reduzir escopo e explicar o que deixou
  de fora a entregar tudo pela metade.
- **Prazo de envio: 3 dias corridos** a partir do recebimento.

Não estamos medindo velocidade. Estamos medindo julgamento, clareza e a
capacidade de comunicar decisões técnicas para públicos diferentes.

## O cenário

A Impulso mantém um produto de gestão da atenção primária usado por equipes de
saúde da família. Uma das telas é a **Lista Nominal de Hipertensão**: a equipe
abre a lista, vê quem está com o acompanhamento atrasado e age — liga, agenda,
prioriza visitas.

O time de produto validou o protótipo da tela e ele foi aprovado. Agora é
preciso construir a tabela que alimenta essa tela.

Você recebeu três arquivos com dados da camada bruta, extraídos do e-SUS PEC
(o prontuário eletrônico da atenção primária). Esses dados **não passaram por
nenhum tratamento**.

## O que está neste pacote

```
contexto/
  01-lista-nominal.md            contexto de domínio: APS, e-SUS PEC, lista nominal
  02-regras-hipertensao.md       regras de negócio a implementar
  03-dicionario-dados.md         documentação das três tabelas
  prototipo-lista-nominal.png    o protótipo aprovado pelo time de produto
dados/
  cidadao_pec.csv                cadastro de cidadãos
  atendimento_individual.csv     atendimentos individuais
  procedimentos.csv              procedimentos, medições e exames
ENTREGAVEIS.md                   o que entregar e em que formato
```

Comece por [contexto/01-lista-nominal.md](contexto/01-lista-nominal.md). Não é
necessário conhecimento prévio de saúde pública.

## O que entregar

Quatro artefatos, detalhados em [ENTREGAVEIS.md](ENTREGAVEIS.md):

1. **Diagrama da arquitetura** do pipeline, do dado bruto à tabela final.
2. **SQL** com a modelagem da tabela final.
3. **Documentação para o time de produto**, explicando as regras adotadas.
4. **Mensagem para o time de engenharia de dados** sobre os problemas
   encontrados nos dados.

Mais uma coisa, que não é um artefato mas é obrigatória: uma **nota sobre uso de
IA** (também descrita em `ENTREGAVEIS.md`).

## Sobre usar IA

**Você pode usar IA à vontade.** Nós usamos. Não há nenhuma penalidade por isso,
e não estamos tentando detectar seu uso.

O que pedimos é que você **descreva como usou** — quais ferramentas, em quais
partes, o que aceitou e o que descartou. Trabalhar bem com IA é parte do
trabalho, e saber onde ela erra é parte de trabalhar bem com ela.

## Como pensar sobre este case

Uma coisa que ajuda a calibrar o esforço: **não existe uma resposta única.**
Várias decisões deste case são genuinamente ambíguas e admitem mais de uma saída
defensável. Nesses pontos, o que avaliamos é a qualidade da justificativa, não a
escolha em si. Deixe as decisões visíveis em vez de escondê-las no código.

## Dúvidas

Se algo estiver ambíguo, você pode perguntar — mas também pode simplesmente
**assumir uma interpretação e registrá-la** na documentação. As duas saídas são
aceitáveis.
