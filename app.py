"""
Lista Nominal — Hipertensão

Front-end Streamlit para a tabela `gold_lista_nominal_hipertensao`, construída
pelo pipeline em sql/01 a sql/06. Roda a partir da raiz do repositório:

    streamlit run app.py

Duas visões:
- "Lista nominal": a tela operacional (mesmo propósito do protótipo em
  contexto/prototipo-lista-nominal.png) — identificação completa, porque é o
  que a equipe de saúde precisa pra agir sobre a pessoa.
- "Painel de cobertura": visão agregada sem identificação, usando a view
  gold_lista_nominal_hipertensao_analitico (ver extras/lgpd-notas.md).
"""

from pathlib import Path

import altair as alt
import duckdb
import pandas as pd
import streamlit as st

ROOT = Path(__file__).parent
DATA_REFERENCIA = "01/08/2026"

# Paleta extraída de impulsogov.org (ver .scratch, computed styles da home).
# Cor semântica de status fica fora dessa paleta de marca por escolha: verde/
# âmbar/vermelho continuam sendo o que uma equipe de saúde reconhece de
# relance — o coral da marca já cai bem perto do âmbar, então ele dá conta de
# "Atrasada" sem sacrificar leitura rápida.
MARCA = {
    "navy": "#114350",
    "teal": "#2EA6BC",
    "teal_claro": "#EAF6F8",
    "teal_tint": "#8FD0DA",
    "coral": "#EF8264",
    "cinza": "#5B7480",
}

STATUS_COR = {
    "EM DIA": "#1F8A70",
    "ATRASADA": MARCA["coral"],
    "NUNCA REALIZADA": "#C13C2E",
}
STATUS_LABEL = {
    "EM DIA": "Em dia",
    "ATRASADA": "Atrasada",
    "NUNCA REALIZADA": "Nunca realizada",
}
FAIXAS_ETARIAS = ["0-17", "18-29", "30-44", "45-59", "60-74", "75+"]

st.set_page_config(page_title="Lista Nominal — Hipertensão", page_icon="🩺", layout="wide")

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}

    h1 {{
        color: {MARCA["navy"]} !important;
        font-weight: 300 !important;
        letter-spacing: -0.01em;
    }}

    [data-testid="stCaptionContainer"] {{ color: {MARCA["cinza"]} !important; }}

    .marca-wordmark {{
        display: flex; align-items: center;
        font-family: 'Inter', sans-serif; font-weight: 800; font-size: 32px;
        letter-spacing: -0.01em;
        margin: 4px 0 18px 0;
    }}

    [data-testid="stTabs"] button[aria-selected="true"] {{
        color: {MARCA["teal"]} !important;
        border-bottom-color: {MARCA["teal"]} !important;
    }}
    [data-testid="stTabs"] button p {{ font-weight: 500; }}

    [data-testid="stMetric"] {{
        background: {MARCA["teal_claro"]};
        border: 1px solid #D8ECEF;
        border-left: 4px solid {MARCA["teal"]};
        border-radius: 10px;
        padding: 14px 16px 8px 16px;
    }}
    [data-testid="stMetricValue"] {{ color: {MARCA["navy"]}; }}
    [data-testid="stMetricLabel"] {{ color: {MARCA["cinza"]}; }}
    /* delta aqui é só a contagem-base (ex. "31 de 49 pessoas"), não uma
       tendência — a setinha de alta/baixa do st.metric não se aplica. */
    [data-testid="stMetricDelta"] svg {{ display: none; }}
    [data-testid="stMetricDelta"] {{ color: {MARCA["cinza"]} !important; }}

    [data-testid="stDataFrame"] {{
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid #E3ECEE;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def build_database() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect(database=":memory:")
    camadas = [
        "sql/01_bronze.sql",
        "sql/02_silver.sql",
        "sql/03_gold.sql",
        "sql/05_privacidade_lgpd.sql",
        "sql/06_guardrails.sql",  # bloqueia a inicialização se algo quebrar
    ]
    for arquivo in camadas:
        con.execute((ROOT / arquivo).read_text(encoding="utf-8"))
    return con


def faixa_etaria(idade: int) -> str:
    if idade < 18:
        return "0-17"
    if idade < 30:
        return "18-29"
    if idade < 45:
        return "30-44"
    if idade < 60:
        return "45-59"
    if idade < 75:
        return "60-74"
    return "75+"


def formata_situacao(status: str, data, valor: str | None = None) -> str:
    if pd.isna(data):
        return STATUS_LABEL[status]
    partes = [STATUS_LABEL[status], pd.Timestamp(data).strftime("%d/%m/%Y")]
    if valor:
        partes.append(f"{valor} mmHg")
    return " · ".join(partes)


def colore_status(valor: str) -> str:
    for chave, cor in STATUS_COR.items():
        if valor.startswith(STATUS_LABEL[chave]):
            return f"color: {cor}; font-weight: 600"
    return ""


try:
    con = build_database()
except Exception as exc:  # guardrail bloqueante disparou, ou erro de pipeline
    st.error(f"O pipeline de dados falhou ao inicializar — dado não é confiável para exibição.\n\n{exc}")
    st.stop()

gold = con.execute("SELECT * FROM gold_lista_nominal_hipertensao").df()
gold["faixa_etaria"] = gold["idade"].apply(faixa_etaria)
gold["documento"] = gold["nu_cns"].where(gold["nu_cns"].notna() & (gold["nu_cns"] != ""), gold["nu_cpf_cidadao"])

WORDMARK = f"""
<div class="marca-wordmark">
    <span style="color:{MARCA["navy"]}">imp</span>
    <svg width="37" height="27" viewBox="0 0 37 27" style="margin: 0 2px 0 3px;">
        <circle cx="12" cy="13.5" r="9" fill="none" stroke="{MARCA["navy"]}" stroke-width="4.5"/>
        <circle cx="24" cy="13.5" r="9" fill="none" stroke="{MARCA["navy"]}" stroke-width="4.5"/>
    </svg>
    <span style="color:{MARCA["navy"]}">ulso</span><span style="color:{MARCA["teal"]}">gov</span>
</div>
"""
st.markdown(WORDMARK, unsafe_allow_html=True)

# ============================================================================
# CONTROLE DE ACESSO — o perfil é o nu_ine da equipe (não existe tabela de
# usuário/login nos dados de origem, então o nu_ine faz esse papel). Um
# perfil de equipe só acessa a própria lista. Existe um segundo perfil,
# "Gestão", sem nu_ine correspondente na base — enxerga todas as equipes e a
# performance global, para comparação e supervisão. Nota de LGPD: dar a esse
# perfil a mesma Lista nominal identificada (não só o Painel agregado) é uma
# escolha real de superfície de exposição — decidimos assim porque um
# coordenador precisa localizar qualquer pessoa em qualquer equipe pra
# supervisionar, base legal equivalente à do perfil de equipe (art. 11, II,
# "f" / art. 7º, III — ver extras/lgpd-notas.md). Vale revisitar se a organização
# quiser um perfil de gestão mais restrito.
# ============================================================================
GESTAO = "GESTAO_GLOBAL"

equipes_disponiveis = (
    gold[["nu_ine", "no_equipe"]]
    .assign(no_equipe=lambda d: d["no_equipe"].str.strip())
    .drop_duplicates()
    .sort_values("no_equipe")
)
equipes_disponiveis["rotulo"] = equipes_disponiveis["no_equipe"] + "  ·  nu_ine " + equipes_disponiveis["nu_ine"]
ROTULO_GESTAO = "Gestão — todas as equipes"

if "nu_ine_logado" not in st.session_state:
    st.session_state.nu_ine_logado = None

if st.session_state.nu_ine_logado is None:
    st.title("Lista Nominal — Hipertensão", anchor=False)
    st.caption("Acesso restrito por perfil")
    st.info(
        "O acesso é condicionado ao perfil — cada equipe só acessa a própria "
        "lista; o perfil de Gestão acessa todas. Selecione seu perfil para entrar. "
        "(Esta é uma simulação do controle de acesso baseada no perfil escolhido, "
        "não uma autenticação real.)"
    )
    rotulo_escolhido = st.selectbox("Seu perfil", [ROTULO_GESTAO] + equipes_disponiveis["rotulo"].tolist())
    if st.button("Entrar", type="primary"):
        if rotulo_escolhido == ROTULO_GESTAO:
            st.session_state.nu_ine_logado = GESTAO
        else:
            st.session_state.nu_ine_logado = equipes_disponiveis.loc[
                equipes_disponiveis["rotulo"] == rotulo_escolhido, "nu_ine"
            ].iloc[0]
        st.rerun()
    st.stop()

eh_gerencial = st.session_state.nu_ine_logado == GESTAO

if eh_gerencial:
    nome_equipe_logada = "Gestão — todas as equipes"
else:
    gold = gold[gold["nu_ine"] == st.session_state.nu_ine_logado].reset_index(drop=True)
    nome_equipe_logada = equipes_disponiveis.loc[
        equipes_disponiveis["nu_ine"] == st.session_state.nu_ine_logado, "no_equipe"
    ].iloc[0]

with st.sidebar:
    st.markdown(WORDMARK, unsafe_allow_html=True)
    st.caption("Perfil logado")
    if eh_gerencial:
        st.markdown(f"**{nome_equipe_logada}**  \nperfil gerencial")
    else:
        st.markdown(f"**{nome_equipe_logada}**  \nnu_ine {st.session_state.nu_ine_logado}")
    if st.button("Trocar de equipe" if not eh_gerencial else "Trocar de perfil"):
        st.session_state.nu_ine_logado = None
        st.rerun()

titulo_pagina = "Painel de Cobertura — Hipertensão" if eh_gerencial else "Lista Nominal — Hipertensão"
st.title(titulo_pagina, anchor=False)
st.caption(f"{nome_equipe_logada} · Acompanhamento das boas práticas por pessoa · posição em {DATA_REFERENCIA}")

# O perfil de gestão não acessa dado sensível/identificado: sem a Lista
# nominal (nome, CPF, CNS, telefone), só o Painel de cobertura agregado —
# mesmo princípio de minimização de dados de extras/lgpd-notas.md, aplicado agora
# também ao controle de acesso do app, não só às views SQL.
if eh_gerencial:
    st.info(
        "Perfil de gestão: acesso apenas a dados agregados e sem identificação. "
        "A Lista nominal (nome, CPF, CNS, telefone) é exclusiva dos perfis de equipe."
    )
    (aba_painel,) = st.tabs(["📊 Painel de cobertura"])
    aba_lista = None
else:
    aba_lista, aba_painel = st.tabs(["📋 Lista nominal", "📊 Painel de cobertura"])

# ============================================================================
# ABA 1 — Lista nominal (visão operacional, identificação completa)
# Só existe para perfis de equipe — ver nota de acesso acima.
# ============================================================================
if aba_lista is not None:
  with aba_lista:
    st.caption(
        f"Você está vendo só a lista da sua equipe ({nome_equipe_logada}) — o "
        "acesso é restrito por perfil (nu_ine), outras equipes não aparecem aqui."
    )
    col2, col3, col4, col5 = st.columns([1.3, 1.3, 1.3, 1])

    with col2:
        st.selectbox(
            "Microárea",
            ["Todas"],
            disabled=True,
            help="Não existe nos dados de origem — ver limitação em entregaveis/03-documentacao-produto.md",
        )
    with col3:
        faixa_sel = st.selectbox("Faixa etária", ["Todas"] + FAIXAS_ETARIAS)
    with col4:
        pelo_menos_uma = st.checkbox("Pelo menos uma a fazer")
    with col5:
        todas_em_dia = st.checkbox("Todas em dia")

    filtrado = gold.copy()
    if faixa_sel != "Todas":
        filtrado = filtrado[filtrado["faixa_etaria"] == faixa_sel]

    status_cols = ["status_consulta", "status_afericao_pressao", "status_peso_altura"]
    if pelo_menos_uma:
        filtrado = filtrado[(filtrado[status_cols] != "EM DIA").any(axis=1)]
    if todas_em_dia:
        filtrado = filtrado[(filtrado[status_cols] == "EM DIA").all(axis=1)]

    total_filtrado = len(filtrado)

    def _pct_e_contagem(mascara) -> tuple[str, str]:
        if not total_filtrado:
            return "—", ""
        n = int(mascara.sum())
        return f"{n / total_filtrado * 100:.0f}%", f"{n} de {total_filtrado} pessoas"

    pct_consulta, n_consulta = _pct_e_contagem(filtrado["status_consulta"] == "EM DIA")
    pct_pressao, n_pressao = _pct_e_contagem(filtrado["status_afericao_pressao"] == "EM DIA")
    pct_peso, n_peso = _pct_e_contagem(filtrado["status_peso_altura"] == "EM DIA")

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Pessoas na lista", total_filtrado)
    k2.metric("Consulta em dia", pct_consulta, delta=n_consulta, delta_color="off")
    k3.metric("Pressão em dia", pct_pressao, delta=n_pressao, delta_color="off")
    k4.metric("Peso/altura em dia", pct_peso, delta=n_peso, delta_color="off")

    st.divider()

    colunas_tabela = {
        "Cidadão": filtrado["no_cidadao"].str.title().fillna("(sem nome cadastrado)"),
        "CNS/CPF": filtrado["documento"],
        "Idade": filtrado["idade"].astype(int).astype(str) + " anos",
        "Telefone": filtrado["nu_telefone_celular"],
    }

    tabela = pd.DataFrame(
        {
            **colunas_tabela,
            "Consulta": [
                formata_situacao(s, d) for s, d in zip(filtrado["status_consulta"], filtrado["dt_ultima_consulta"])
            ],
            "Aferição de pressão": [
                formata_situacao(s, d, v)
                for s, d, v in zip(
                    filtrado["status_afericao_pressao"],
                    filtrado["dt_ultima_afericao_pressao"],
                    filtrado["valor_ultima_afericao_pressao"],
                )
            ],
            "Peso e altura": [
                formata_situacao(s, d) for s, d in zip(filtrado["status_peso_altura"], filtrado["dt_ultimo_peso_altura"])
            ],
        }
    )

    estilo = tabela.style.map(colore_status, subset=["Consulta", "Aferição de pressão", "Peso e altura"])
    st.dataframe(estilo, use_container_width=True, hide_index=True, height=560)

# ============================================================================
# ABA 2 — Painel de cobertura (agregado, sem identificação — LGPD)
# ============================================================================
with aba_painel:
    if eh_gerencial:
        st.caption(
            "Performance global — todas as equipes. Sem nome, documento ou "
            "telefone, mesmo para o perfil de gestão. Usa "
            "gold_lista_nominal_hipertensao_analitico (ver extras/lgpd-notas.md, princípio de "
            "minimização de dados)."
        )
    else:
        st.caption(
            f"Cobertura da equipe {nome_equipe_logada} — mesmo controle de acesso da Lista "
            "nominal (por nu_ine), aqui sem nome, documento ou telefone. Usa "
            "gold_lista_nominal_hipertensao_analitico (ver extras/lgpd-notas.md, princípio de "
            "minimização de dados)."
        )

    analitico = con.execute("SELECT * FROM gold_lista_nominal_hipertensao_analitico").df()
    if not eh_gerencial:
        analitico = analitico[analitico["nu_ine"] == st.session_state.nu_ine_logado].reset_index(drop=True)

    # "Nunca realizada" não existe de fato para Consulta — o critério de
    # entrada na lista já exige uma consulta (guardrail G4 em
    # sql/06_guardrails.sql) — então essa combinação simplesmente não entra
    # nos dados abaixo, em vez de aparecer como barra zerada.
    ordem_completa = ["Em dia", "Atrasada", "Nunca realizada"]
    ordem_praticas = ["Consulta", "Aferição de pressão", "Peso e altura"]
    escala_status = alt.Scale(
        domain=ordem_completa,
        range=[STATUS_COR["EM DIA"], STATUS_COR["ATRASADA"], STATUS_COR["NUNCA REALIZADA"]],
    )

    total_cobertura = len(analitico)
    linhas = []
    for coluna, titulo, status_validos in [
        ("status_consulta", "Consulta", ordem_completa[:2]),
        ("status_afericao_pressao", "Aferição de pressão", ordem_completa),
        ("status_peso_altura", "Peso e altura", ordem_completa),
    ]:
        contagem = analitico[coluna].map(STATUS_LABEL).value_counts().reindex(status_validos).fillna(0)
        for status, pessoas in contagem.items():
            pessoas = int(pessoas)
            pct = round(pessoas / total_cobertura * 100) if total_cobertura else 0
            linhas.append(
                {
                    "pratica": titulo,
                    "status": status,
                    "pessoas": pessoas,
                    "pct": pct,
                    "total": total_cobertura,
                    "rotulo": f"{pessoas} · {pct}%",
                }
            )
    dados_cobertura = pd.DataFrame(linhas)

    subtitulo_escopo = "Todas as equipes" if eh_gerencial else f"Equipe {nome_equipe_logada}"
    titulo_grafico = alt.TitleParams(
        text="Cobertura por boa prática",
        subtitle=f"{subtitulo_escopo} · posição em {DATA_REFERENCIA}",
        color=MARCA["navy"],
        subtitleColor=MARCA["cinza"],
        fontSize=16,
        fontWeight=700,
        subtitleFontSize=12,
        anchor="start",
        offset=12,
    )
    barras_cobertura = (
        alt.Chart(dados_cobertura, title=titulo_grafico)
        .mark_bar()
        .encode(
            x=alt.X(
                "pratica:N",
                sort=ordem_praticas,
                title=None,
                axis=alt.Axis(
                    labelFontSize=18,
                    labelFontWeight=700,
                    labelColor=MARCA["navy"],
                    labelAngle=0,
                    labelLimit=200,
                    orient="top",
                ),
            ),
            xOffset=alt.XOffset("status:N", sort=ordem_completa),
            y=alt.Y("pessoas:Q", title="Pessoas"),
            color=alt.Color(
                "status:N",
                scale=escala_status,
                sort=ordem_completa,
                title="Status",
                legend=alt.Legend(orient="left"),
            ),
            tooltip=[
                "pratica",
                "status",
                alt.Tooltip("pessoas:Q", title="Pessoas"),
                alt.Tooltip("pct:Q", title="% da lista"),
                alt.Tooltip("total:Q", title="Comprimento (pessoas da lista)"),
            ],
        )
    )
    labels_cobertura = (
        alt.Chart(dados_cobertura)
        .mark_text(dy=-8, fontSize=11, fontWeight=700, color=MARCA["navy"])
        .encode(
            x=alt.X("pratica:N", sort=ordem_praticas),
            xOffset=alt.XOffset("status:N", sort=ordem_completa),
            y=alt.Y("pessoas:Q"),
            text="rotulo:N",
        )
    )
    st.altair_chart(
        (barras_cobertura + labels_cobertura).properties(height=380, title=titulo_grafico),
        use_container_width=True,
    )

    # Análise gerada a partir dos mesmos dados do gráfico — recalcula pra
    # cada equipe logada, não é texto fixo.
    resumo = dados_cobertura.pivot_table(
        index="pratica", columns="status", values="pessoas", aggfunc="sum", fill_value=0
    )
    for coluna_status in ordem_completa:
        if coluna_status not in resumo.columns:
            resumo[coluna_status] = 0
    total_equipe = len(analitico)
    resumo["pct_em_dia"] = (resumo["Em dia"] / total_equipe * 100).round(0) if total_equipe else 0

    pior = resumo["pct_em_dia"].idxmin()
    melhor = resumo["pct_em_dia"].idxmax()
    pior_pct = int(resumo.loc[pior, "pct_em_dia"])
    melhor_pct = int(resumo.loc[melhor, "pct_em_dia"])
    pior_nunca = int(resumo.loc[pior, "Nunca realizada"])

    escopo_texto = "de todas as equipes" if eh_gerencial else "da equipe"
    analise = (
        f"Das <strong>{total_equipe} pessoas</strong> {escopo_texto}, "
        f"<strong>{pior}</strong> é a boa prática com menor cobertura — só "
        f"<strong>{pior_pct}%</strong> estão em dia"
    )
    if pior_nunca > 0:
        analise += (
            f", e <strong>{pior_nunca}</strong> nunca tiveram essa medida registrada "
            "mesmo já tendo passado por consulta"
        )
    analise += f". <strong>{melhor}</strong> é a mais em dia, com {melhor_pct}%."
    if pior != melhor:
        grupo_texto = "entre as equipes" if eh_gerencial else "não na equipe como um todo"
        analise += (
            f" A diferença de {melhor_pct - pior_pct} pontos percentuais sugere que o "
            f"gargalo está especificamente em {pior.lower()}, {grupo_texto}."
        )

    st.markdown(
        f"""
        <div style="background:{MARCA["teal_claro"]}; border-left:4px solid {MARCA["teal"]};
                    border-radius:8px; padding:14px 18px; margin-top:16px;">
            <span style="font-weight:700; color:{MARCA["navy"]}; display:block; margin-bottom:4px;">
                Leitura do gráfico
            </span>
            <span style="color:{MARCA["navy"]};">{analise}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ========================================================================
    # Comparação entre equipes — só para o perfil de gestão. Perfis de
    # equipe não têm essa visão: não faz sentido comparar quem eles não
    # conseguem ver.
    # ========================================================================
    if eh_gerencial:
        st.divider()

        # Agrupar por no_equipe quebraria de novo o caso real de dois nu_ine
        # com o mesmo nome ("ESF 5") — guardrail S7 em sql/06_guardrails.sql.
        # A chave de agrupamento é sempre nu_ine; o rótulo só acrescenta o
        # nu_ine ao nome quando existe mais de um nu_ine com o mesmo nome.
        mapa_equipe = (
            analitico[["nu_ine", "no_equipe"]]
            .assign(no_equipe=lambda d: d["no_equipe"].str.strip())
            .drop_duplicates()
        )
        mapa_equipe["duplicado"] = mapa_equipe.groupby("no_equipe")["nu_ine"].transform("nunique") > 1
        mapa_equipe["rotulo_equipe"] = mapa_equipe["no_equipe"]
        mapa_equipe.loc[mapa_equipe["duplicado"], "rotulo_equipe"] = (
            mapa_equipe["no_equipe"] + " (" + mapa_equipe["nu_ine"].str[-4:] + ")"
        )
        analitico = analitico.merge(mapa_equipe[["nu_ine", "rotulo_equipe"]], on="nu_ine", how="left")

        todas_equipes_regua = sorted(analitico["rotulo_equipe"].unique())
        indice_completo = pd.MultiIndex.from_product(
            [todas_equipes_regua, ordem_completa], names=["equipe", "status"]
        )
        linhas_regua = []
        for coluna_status, titulo in [
            ("status_consulta", "Consulta"),
            ("status_afericao_pressao", "Aferição de pressão"),
            ("status_peso_altura", "Peso e altura"),
        ]:
            tmp = analitico.assign(
                equipe=analitico["rotulo_equipe"],
                status=analitico[coluna_status].map(STATUS_LABEL),
            )
            contagem = (
                tmp.groupby(["equipe", "status"]).size().reindex(indice_completo, fill_value=0)
                .rename("pessoas")
                .reset_index()
            )
            contagem["pratica"] = titulo
            linhas_regua.append(contagem)
        dados_regua = pd.concat(linhas_regua, ignore_index=True)
        dados_regua["ordem_status"] = dados_regua["status"].map(
            {s: i for i, s in enumerate(ordem_completa)}
        )
        totais_equipe = dados_regua.groupby("equipe")["pessoas"].sum().div(3)  # 3 práticas somadas
        dados_regua = dados_regua.merge(
            totais_equipe.rename("total").reset_index(), on="equipe", how="left"
        )
        # % de cada status sobre o total da equipe — comparável entre equipes
        # de tamanhos diferentes (38 a 83 pessoas), o que a contagem
        # absoluta sozinha não é.
        dados_regua["pct"] = (dados_regua["pessoas"] / dados_regua["total"] * 100).round(0)
        dados_regua["pct_label"] = dados_regua["pct"].astype(int).astype(str) + "%"

        max_total = totais_equipe.max()
        ordem_equipes_regua = totais_equipe.sort_values(ascending=False).index.tolist()

        # Sem subtitle aqui de propósito: num facet, o Vega-Lite repete
        # title+subtitle em cada uma das 3 colunas. A explicação vai só uma
        # vez, como caption, depois do gráfico.
        titulo_regua = alt.TitleParams(
            text="Cobertura por equipe",
            color=MARCA["navy"],
            fontSize=16,
            fontWeight=700,
            anchor="start",
            offset=12,
        )

        reguas = (
            alt.Chart(dados_regua)
            .mark_bar(height=16, cornerRadius=2)
            .encode(
                x=alt.X("pessoas:Q", title=None, axis=None, scale=alt.Scale(domain=[0, max_total]), stack="zero"),
                y=alt.Y("equipe:N", sort=ordem_equipes_regua, title=None),
                order=alt.Order("ordem_status:Q"),
                color=alt.Color(
                    "status:N",
                    scale=escala_status,
                    sort=ordem_completa,
                    title="Status",
                    legend=alt.Legend(orient="left"),
                ),
                tooltip=[
                    "equipe",
                    "pratica",
                    "status",
                    alt.Tooltip("pessoas:Q", title="Pessoas"),
                    alt.Tooltip("pct:Q", title="% da lista vinculada à equipe", format=".0f"),
                    alt.Tooltip("total:Q", title="Comprimento (pessoas da lista)"),
                ],
            )
        )
        total_no_fim = (
            alt.Chart(dados_regua)
            .transform_filter(alt.datum.status == "Em dia")
            .mark_text(dx=6, fontSize=11, fontWeight=700, color=MARCA["navy"], align="left")
            .encode(
                x=alt.X("total:Q", scale=alt.Scale(domain=[0, max_total])),
                y=alt.Y("equipe:N", sort=ordem_equipes_regua),
                text=alt.Text("pct_label:N"),
            )
        )

        grade_reguas = (
            (reguas + total_no_fim)
            .properties(height=alt.Step(24), width=280, title=titulo_regua)
            .facet(
                column=alt.Column(
                    "pratica:N",
                    sort=ordem_praticas,
                    title=None,
                    header=alt.Header(labelFontSize=18, labelFontWeight=700, labelColor=MARCA["navy"]),
                )
            )
            .resolve_scale(y="shared")
        )
        st.altair_chart(grade_reguas, use_container_width=True)
        st.caption(
            "Comprimento = pessoas da lista vinculadas à equipe; número = % em dia. "
            "Passe o mouse para ver as contagens."
        )

        # Análise por equipe — recalculada a partir dos mesmos dados da régua.
        resumo_equipe = (
            dados_regua.pivot_table(index=["equipe", "pratica"], columns="status", values="pessoas", fill_value=0)
            .reset_index()
        )
        for coluna_status in ordem_completa:
            if coluna_status not in resumo_equipe.columns:
                resumo_equipe[coluna_status] = 0
        resumo_equipe = resumo_equipe.merge(
            dados_regua[["equipe", "pratica", "total"]].drop_duplicates(), on=["equipe", "pratica"]
        )
        # A régua não mostra nenhuma "média das três práticas" em lugar
        # nenhum — cada régua tem UM número, o % daquela prática específica.
        # Uma média entre práticas é um dado que não existe visualmente no
        # gráfico, então o texto não pode se apoiar nela: quem olha a régua
        # não consegue achar "40%" em canto nenhum pra conferir. A leitura
        # abaixo descreve só o que está literalmente desenhado: a pior e a
        # melhor combinação equipe × prática da grade inteira.
        resumo_equipe["pct_exato"] = resumo_equipe["Em dia"] / resumo_equipe["total"] * 100
        resumo_equipe["pct_em_dia"] = resumo_equipe["pct_exato"].round(0).astype(int)

        linha_pior = resumo_equipe.loc[resumo_equipe["pct_exato"].idxmin()]
        linha_melhor = resumo_equipe.loc[resumo_equipe["pct_exato"].idxmax()]

        # Nunca combinar as duas contagens de "Nunca realizada" (pressão e
        # peso/altura) num total só — nem soma (duplica quem está nas duas)
        # nem união (não aparece em lugar nenhum da régua pra conferir).
        # Reporta as duas contagens separadas, cada uma é literalmente o
        # rótulo/tooltip de um segmento específico da régua.
        nunca_pressao_por_equipe = (
            resumo_equipe[resumo_equipe["pratica"] == "Aferição de pressão"]
            .set_index("equipe")["Nunca realizada"]
        )
        nunca_peso_por_equipe = (
            resumo_equipe[resumo_equipe["pratica"] == "Peso e altura"]
            .set_index("equipe")["Nunca realizada"]
        )
        equipe_mais_nunca_pressao = nunca_pressao_por_equipe.idxmax()
        valor_mais_nunca_pressao = int(nunca_pressao_por_equipe[equipe_mais_nunca_pressao])
        equipe_mais_nunca_peso = nunca_peso_por_equipe.idxmax()
        valor_mais_nunca_peso = int(nunca_peso_por_equipe[equipe_mais_nunca_peso])

        equipe_pior_cel, pratica_pior_cel, pct_pior_cel = (
            linha_pior["equipe"], linha_pior["pratica"], int(linha_pior["pct_em_dia"])
        )
        equipe_melhor_cel, pratica_melhor_cel, pct_melhor_cel = (
            linha_melhor["equipe"], linha_melhor["pratica"], int(linha_melhor["pct_em_dia"])
        )

        # "Pior" e "melhor" célula quase sempre vêm de equipe E prática
        # diferentes (é o caso aqui: ESF 1 em peso/altura vs. ESF 5 em
        # consulta) — a diferença entre as duas não é "a distância entre
        # essas equipes", é a amplitude da grade inteira. Comparar como se
        # fosse um confronto direto entre duas equipes seria enganoso,
        # porque práticas diferentes têm níveis de cobertura diferentes por
        # natureza (consulta é sempre mais fácil de manter em dia que
        # peso/altura, pra qualquer equipe).
        mesma_pratica = pratica_pior_cel == pratica_melhor_cel
        analise_equipe = (
            f"A régua mais fraca da grade é <strong>{equipe_pior_cel}</strong> em "
            f"<strong>{pratica_pior_cel.lower()}</strong>, com só <strong>{pct_pior_cel}%</strong> em dia. "
            f"A mais forte é <strong>{equipe_melhor_cel}</strong> em "
            f"<strong>{pratica_melhor_cel.lower()}</strong>, com <strong>{pct_melhor_cel}%</strong>"
        )
        if mesma_pratica:
            analise_equipe += (
                f" — {pct_melhor_cel - pct_pior_cel} pontos de diferença entre as duas equipes "
                f"na mesma prática."
            )
        else:
            analise_equipe += (
                f". São {pct_melhor_cel - pct_pior_cel} pontos de amplitude entre o pior e o "
                "melhor resultado da grade — não é uma comparação direta entre as duas equipes, "
                "já que são práticas diferentes (consulta tende a ter cobertura mais alta que "
                "peso/altura em qualquer equipe)."
            )
        if equipe_mais_nunca_pressao == equipe_mais_nunca_peso:
            analise_equipe += (
                f" <strong>{equipe_mais_nunca_pressao}</strong> é quem mais tem gente nunca avaliada "
                f"nas duas práticas: <strong>{valor_mais_nunca_pressao}</strong> nunca mediram pressão e "
                f"<strong>{valor_mais_nunca_peso}</strong> nunca tiveram peso/altura registrados."
            )
        else:
            analise_equipe += (
                f" Em nunca mediu pressão, quem mais tem é <strong>{equipe_mais_nunca_pressao}</strong> "
                f"(<strong>{valor_mais_nunca_pressao}</strong> pessoas); em nunca teve peso/altura "
                f"registrado, é <strong>{equipe_mais_nunca_peso}</strong> "
                f"(<strong>{valor_mais_nunca_peso}</strong> pessoas)."
            )

        st.markdown(
            f"""
            <div style="background:{MARCA["teal_claro"]}; border-left:4px solid {MARCA["teal"]};
                        border-radius:8px; padding:14px 18px; margin-top:16px;">
                <span style="font-weight:700; color:{MARCA["navy"]}; display:block; margin-bottom:4px;">
                    Leitura por equipe
                </span>
                <span style="color:{MARCA["navy"]};">{analise_equipe}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
