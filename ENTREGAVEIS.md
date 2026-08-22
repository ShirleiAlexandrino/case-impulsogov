# Entregáveis

## O contexto

A Impulso mantém um produto de gestão da atenção primária usado por equipes de
saúde da família. Uma das telas é a **Lista Nominal de Hipertensão**: a equipe
abre a lista, vê quem está com o acompanhamento atrasado e age — liga para a
pessoa, agenda consulta, prioriza a visita do agente comunitário.

O protótipo dessa tela já foi validado com o time de produto e está em
[contexto/prototipo-lista-nominal.png](contexto/prototipo-lista-nominal.png).
Falta construir a tabela que alimenta a tela.

Você recebeu três arquivos com dados da camada bruta, extraídos do e-SUS PEC (o
prontuário eletrônico da atenção primária), em
[dados/](dados/). Esses dados **não passaram por nenhum
tratamento**. As regras de negócio a aplicar estão em
[contexto/02-regras-hipertensao.md](contexto/02-regras-hipertensao.md), e o
contexto de domínio — para quem nunca trabalhou com saúde pública — em
[contexto/01-lista-nominal.md](contexto/01-lista-nominal.md).

Sua tarefa é levar esse dado bruto até a tabela final, e comunicar o que fez
para dois públicos diferentes: o time de produto e o time de engenharia de
dados.

## O que entregar

| # | Entregável | Formato |
|---|---|---|
| 1 | **Diagrama da arquitetura do pipeline** — as camadas, o schema da tabela final e onde cada regra é aplicada | livre, 1 página |
| 2 | **SQL da modelagem** — o código que produz a tabela final a partir dos CSVs, mais os números que ele devolve | dialeto livre |
| 3 | **Documentação para o time de produto** — regras adotadas, decisões ambíguas e seu impacto, limitações e recomendações | máx. 2 páginas |
| 4 | **Mensagem para o time de engenharia de dados** — os problemas encontrados nos dados, priorizados | Slack ou e-mail, máx. ~400 palavras |
| 5 | **Nota sobre uso de IA** — obrigatória | máx. meia página |



## Como enviar

Um arquivo zip ou um repositório Git (público ou com acesso concedido) ou

Formatos livres, exceto onde indicado. Prefira Markdown a PDF para textos.

**Esforço esperado: até 5 horas.** Se estiver passando muito disso, prefira
reduzir escopo e explicar o que deixou de fora a entregar tudo pela metade.

---

## 1. Diagrama da arquitetura do pipeline

Como você levaria o dado bruto até a tabela que alimenta a tela.

Precisa deixar claro:

- **As camadas** do pipeline e o que acontece em cada uma.
- **O schema da tabela final**: nome das colunas, tipos de dados, chave primária,
  granularidade.
- **Onde cada regra de negócio é aplicada** e por que naquela camada.

Formato livre: Mermaid, Excalidraw, draw.io, imagem. Uma página.
O diagrama pode vir acompanhado de texto curto, o que importa é que dê para
entender a proposta sem você presente para explicar.

---

## 2. SQL da modelagem

O código que produz a tabela final a partir dos três CSVs.

- **Dialeto livre** — PostgreSQL, DuckDB, BigQuery, ou o que preferir. Diga qual
  escolheu.
- Deve **rodar sobre os arquivos fornecidos**. 
- Se você usa dbt ou ferramenta equivalente no dia a dia e quiser estruturar
  assim, fique à vontade, mas não é obrigatório e não conta pontos por si só.

Não esperamos otimização de performance: o volume aqui é pequeno de propósito.

**Junto com o SQL, informe os números que ele produziu:**

- **Quantas pessoas ficaram na lista.**
- **Como se distribuem os status** de cada uma das três boas práticas — quantas
  pessoas em dia, atrasadas e nunca realizadas.

Uma tabela curta basta. Não existe um número certo que estejamos esperando.

---

## 3. Documentação para o time de produto

O público é o time de produto: entende de saúde e do produto, não lê SQL.

Deve cobrir:

- **As regras de negócio que você adotou**, em linguagem de negócio.
- **As decisões ambíguas**: onde havia mais de um caminho defensável, qual você
  escolheu, **qual você descartou e por quê**. 
- **Limitações** do que foi entregue.
- **Recomendações** de ajustes ou melhorias que você considere relevantes, no produto ou no dado.

Máximo de 2 páginas.

---

## 4. Mensagem para o time de engenharia de dados

Se você encontrou problemas nos dados. Escreva a mensagem que enviaria ao time
responsável pela origem.

- **Formato de mensagem real** — Slack ou e-mail, como você escreveria de fato.
- **Priorize.** Se você encontrou vários problemas, diga quais **três** levaria
  primeiro e por quê. 
- **Máximo de ~400 palavras.**


Estamos avaliando comunicação escrita com um time par. 

---

## 5. Nota sobre uso de IA (obrigatória)

Meia página, no formato que preferir. Responda:

- Quais ferramentas de IA você usou e em quais partes do case.
- O que você **aceitou** do que ela produziu, e o que **rejeitou ou corrigiu**.
- **Um exemplo concreto** de algo que a IA errou, ou que você teve que ajustar,
  e como percebeu.

Se você não usou IA, diga isso, é uma resposta válida e não penaliza.

---

