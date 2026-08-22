# Lista Nominal de Hipertensão — notas para o time de produto

Esta tabela alimenta a tela da Lista Nominal de Hipertensão. Para cada pessoa
elegível, ela traz os dados de identificação e contato e a situação das três
boas práticas de acompanhamento, com posição em **01/08/2026** — a data do
retrato de dados analisado. A cada nova carga (as cargas são mensais), a
tabela é recalculada com uma nova data de referência.

Neste retrato, **325 pessoas** estão na lista.

## Quem entra e quem sai da lista

**Entra** quem já teve, em qualquer momento do histórico, um diagnóstico de
hipertensão registrado por médico ou enfermeiro. Não há prazo de validade: é
condição crônica, então um diagnóstico de anos atrás continua valendo.

**Sai** quem faleceu, ou cujo registro mais recente relacionado à hipertensão
é uma marcação de "condição resolvida" feita pelo profissional.

## As três boas práticas

| Boa prática | Prazo considerado | Quem conta |
|---|---|---|
| Consulta | últimos 6 meses | médico ou enfermeiro |
| Aferição de pressão | últimos 6 meses | médico, enfermeiro ou técnico de enfermagem |
| Peso e altura (no mesmo dia) | últimos 12 meses | os anteriores + agente comunitário de saúde |

Cada uma recebe um dos três status: **Em dia** (último registro dentro do
prazo), **Atrasada** (existe registro, mas fora do prazo) ou **Nunca
realizada** (não existe nenhum registro no histórico). Uma observação: "Nunca
realizada" nunca vai aparecer para Consulta — o próprio critério de entrada na
lista já exige que a pessoa tenha tido uma consulta com médico ou enfermeiro,
então esse cruzamento é impossível por definição, não um erro na tela.

## Decisões ambíguas

**1. Reabertura de caso.** Encontramos pessoas marcadas como "condição
resolvida" e, depois, diagnosticadas novamente com hipertensão — um caso real
neste retrato, não hipotético. Adotamos a regra "o registro mais recente
manda": se a pessoa foi rediagnosticada, ela volta para a lista. Descartamos a
alternativa "resolvida uma vez, sai para sempre", porque isso deixaria
pessoas com hipertensão ativa sem acompanhamento — o oposto do que a lista
existe para fazer.

**2. Território / microárea.** O protótipo tem um filtro por microárea, mas
esse dado não existe nos arquivos recebidos — só temos a equipe de saúde da
família, que é um nível acima. Avaliamos aproximar a microárea a partir do
DDD do telefone da pessoa, e descartamos: DDD é código de telefonia, sem
relação com o território sanitário — nos dados, nem a própria equipe da
pessoa tem DDD consistente. Preferimos não ter o filtro a ter um filtro que
agrupa gente errada, numa ferramenta cujo uso é decidir quem visitar.

## Limitações

- **Sem filtro por microárea** (ver decisão acima). O filtro por equipe
  continua disponível.
- **Idade calculada em relação a 01/08/2026**, não à data em que a tela é
  aberta. A cada atualização de dados, precisa ser recalculada junto.
- **O valor da pressão é exibido cru**, como veio do registro (ex. "150/70").
  Não há hoje nenhum destaque para leituras em faixa de crise hipertensiva —
  ver recomendação abaixo.
- **Consistência de nomes de equipe**: encontramos o mesmo código de equipe
  grafado de formas diferentes entre cargas (ex. "ESF 2" e "Esf 2"); tratamos
  isso no pipeline, mas é um sintoma de qualidade de dado na origem, não algo
  que o produto precise resolver.
- **Duas equipes reais compartilham o mesmo nome.** Existem duas equipes
  distintas — com código estável (`nu_ine`) diferente, cadastro diferente —
  ambas chamadas "ESF 5" na base. Qualquer filtro ou relatório que agrupe
  por **nome** da equipe, em vez do código, mistura as duas sem aviso.
  Tratamos isso no app usando sempre o código como identidade (o nome mostrado
  fica com um sufixo quando há esse conflito), mas vale o time de produto
  saber que "nome da equipe" nunca deveria ser tratado como identificador
  único em nenhuma tela ou relatório futuro.

## Recomendações

1. **Pedir ao time de engenharia de dados** para confirmar se a microárea
   pode ser incluída na próxima extração — ela é registrada operacionalmente
   pelo agente comunitário de saúde no e-SUS PEC, então é provável que só não
   tenha vindo nesta base.
2. **Considerar destacar visualmente** quando a última aferição de pressão
   estiver em faixa de crise hipertensiva (ex. sistólica ≥ 180 ou diastólica
   ≥ 120), para priorização imediata pela equipe. Hoje só mostramos o valor,
   sem nenhum sinal de urgência — é uma melhoria de produto, não algo que os
   dados brutos já resolvem sozinhos.
3. **Alinhar a cadência de atualização** com quem vai usar a tela: como a
   base é recarregada mensalmente, vale deixar claro para o time (e talvez
   para o usuário final) qual é a "idade" máxima da informação exibida.
4. **Nunca usar nome de equipe como identificador em telas ou relatórios
   futuros** — usar sempre o código (`nu_ine`). O caso das duas equipes
   "ESF 5" mostra que o nome sozinho já causa erro real hoje, e provavelmente
   vai continuar acontecendo enquanto o cadastro permitir nomes duplicados.
