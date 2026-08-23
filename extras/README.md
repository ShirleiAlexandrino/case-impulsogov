# Extras

Escopo além do pedido em [`../ENTREGAVEIS.md`](../ENTREGAVEIS.md) — não é
necessário pra avaliar os cinco entregáveis oficiais (ver
[`../entregaveis/`](../entregaveis/)).

- [`lgpd-notas.md`](lgpd-notas.md) — classificação do dado, base legal e as
  camadas de minimização aplicadas em [`../sql/05_privacidade_lgpd.sql`](../sql/05_privacidade_lgpd.sql),
  mais o controle de acesso por perfil implementado em [`../app.py`](../app.py).
- [`arquitetura-togaf.md`](arquitetura-togaf.md) — arquitetura TOGAF (BDAT) da
  solução inteira (pipeline + LGPD + guardrails + app + deploy), mais completa
  que o diagrama do entregável 1, que cobre só o pipeline.
- [`../sql/06_guardrails.sql`](../sql/06_guardrails.sql) — checagens de
  qualidade por camada (bloqueantes e informativas).
- [`../app.py`](../app.py) — front-end Streamlit com seleção/simulação de
  perfil por `nu_ine` e dois perfis (equipe / gestão), publicado em
  https://case-impulsogov-shirlei-alexandrino.streamlit.app/.
