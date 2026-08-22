-- ============================================================================
-- CAMADA GOLD — tabela final: Lista Nominal de Hipertensão
-- Granularidade: 1 linha por cidadão elegível.
-- Regras de negócio: contexto/02-regras-hipertensao.md
--
-- Data de referência fixa do retrato dos dados (não CURRENT_DATE):
--   2026-08-01
-- ============================================================================

CREATE OR REPLACE TABLE gold_lista_nominal_hipertensao AS
WITH
-- Famílias de CBO habilitadas por regra de negócio.
cbo_medico_enfermeiro AS (
    SELECT unnest(['2231','2251','2252','2253','2235']) AS cbo_familia
),
cbo_pressao AS (
    SELECT unnest(['2231','2251','2252','2253','2235','3222']) AS cbo_familia
),
cbo_peso_altura AS (
    SELECT unnest(['2231','2251','2252','2253','2235','3222','5151']) AS cbo_familia
),

-- Eventos de diagnóstico/resolução de hipertensão, só por médico/enfermeiro.
eventos_hipertensao AS (
    SELECT
        a.co_fat_cidadao_pec,
        a.dt_registro,
        a.atend_ind_classificacao
    FROM silver_atendimento_individual a
    WHERE a.atend_ind_classificacao IN ('HIPERTENSÃO', 'HIPERTENSÃO - CONDIÇÃO RESOLVIDA')
      AND a.cbo_familia IN (SELECT cbo_familia FROM cbo_medico_enfermeiro)
),

-- Status mais recente de cada pessoa entre os eventos acima.
--
-- DECISÃO (ambígua, documentada): usamos a classificação do evento mais
-- recente, não "alguma vez foi resolvida". A base contém casos reais de
-- pessoas marcadas como HIPERTENSÃO - CONDIÇÃO RESOLVIDA e, depois,
-- re-diagnosticadas com HIPERTENSÃO (ex. co_fat_cidadao_pec 700331-700353) —
-- clinicamente isso é uma reabertura do quadro, então tratamos como pessoa
-- ativa na lista. A alternativa descartada — "resolvida uma vez, sai para
-- sempre" — ignoraria essa reabertura e deixaria a pessoa sem acompanhamento.
status_mais_recente AS (
    SELECT
        co_fat_cidadao_pec,
        atend_ind_classificacao AS classificacao_mais_recente
    FROM eventos_hipertensao
    QUALIFY row_number() OVER (
        PARTITION BY co_fat_cidadao_pec
        ORDER BY dt_registro DESC
    ) = 1
),

-- Critério de entrada: pelo menos um diagnóstico de hipertensão no histórico.
-- Critério de saída: faleceu, ou o evento mais recente é "condição resolvida".
elegiveis AS (
    SELECT c.co_fat_cidadao_pec
    FROM silver_cidadao c
    JOIN status_mais_recente s ON s.co_fat_cidadao_pec = c.co_fat_cidadao_pec
    WHERE NOT c.faleceu
      AND s.classificacao_mais_recente = 'HIPERTENSÃO'
),

-- Boa prática 1 — Consulta: qualquer atendimento individual, médico ou
-- enfermeiro, últimos 6 meses. Qualquer classificação, qualquer local.
ultima_consulta AS (
    SELECT
        a.co_fat_cidadao_pec,
        max(a.dt_registro) AS dt_ultima_consulta
    FROM silver_atendimento_individual a
    WHERE a.cbo_familia IN (SELECT cbo_familia FROM cbo_medico_enfermeiro)
    GROUP BY a.co_fat_cidadao_pec
),

-- Boa prática 2 — Aferição de pressão arterial: médico, enfermeiro ou
-- técnico/auxiliar de enfermagem, últimos 6 meses. O protótipo mostra o
-- valor da aferição junto da data (ex. "110/90 mmHg"), então trazemos o
-- valor da leitura mais recente, não só a data.
ultima_afericao_pressao AS (
    SELECT
        p.co_fat_cidadao_pec,
        p.dt_registro       AS dt_ultima_afericao_pressao,
        p.pressao_arterial  AS valor_ultima_afericao_pressao
    FROM silver_procedimentos p
    WHERE p.ds_proced = 'AFERIÇÃO DE PRESSÃO ARTERIAL'
      AND p.cbo_familia IN (SELECT cbo_familia FROM cbo_pressao)
    QUALIFY row_number() OVER (
        PARTITION BY p.co_fat_cidadao_pec
        ORDER BY p.dt_registro DESC
    ) = 1
),

-- Boa prática 3 — Peso e altura no mesmo dia: médico, enfermeiro, técnico ou
-- ACS, últimos 12 meses. Só conta quando as duas medidas vêm preenchidas.
ultimo_peso_altura AS (
    SELECT
        p.co_fat_cidadao_pec,
        max(p.dt_registro) AS dt_ultimo_peso_altura
    FROM silver_procedimentos p
    WHERE p.ds_proced = 'MEDIÇÃO PESO E ALTURA'
      AND p.peso_kg IS NOT NULL
      AND p.altura_cm IS NOT NULL
      AND p.cbo_familia IN (SELECT cbo_familia FROM cbo_peso_altura)
    GROUP BY p.co_fat_cidadao_pec
)

SELECT
    c.co_fat_cidadao_pec,
    c.no_cidadao,
    c.nu_cns,
    c.nu_cpf_cidadao,
    c.dt_registro_nascimento,
    date_part('year', age(DATE '2026-08-01', c.dt_registro_nascimento)) AS idade,
    c.nu_telefone_celular,
    c.nu_ine,
    c.no_equipe,

    uc.dt_ultima_consulta,
    CASE
        WHEN uc.dt_ultima_consulta IS NULL THEN 'NUNCA REALIZADA'
        WHEN uc.dt_ultima_consulta >= DATE '2026-08-01' - INTERVAL 6 MONTH THEN 'EM DIA'
        ELSE 'ATRASADA'
    END AS status_consulta,

    up.dt_ultima_afericao_pressao,
    up.valor_ultima_afericao_pressao,
    CASE
        WHEN up.dt_ultima_afericao_pressao IS NULL THEN 'NUNCA REALIZADA'
        WHEN up.dt_ultima_afericao_pressao >= DATE '2026-08-01' - INTERVAL 6 MONTH THEN 'EM DIA'
        ELSE 'ATRASADA'
    END AS status_afericao_pressao,

    upa.dt_ultimo_peso_altura,
    CASE
        WHEN upa.dt_ultimo_peso_altura IS NULL THEN 'NUNCA REALIZADA'
        WHEN upa.dt_ultimo_peso_altura >= DATE '2026-08-01' - INTERVAL 12 MONTH THEN 'EM DIA'
        ELSE 'ATRASADA'
    END AS status_peso_altura

FROM elegiveis e
JOIN silver_cidadao c ON c.co_fat_cidadao_pec = e.co_fat_cidadao_pec
LEFT JOIN ultima_consulta uc          ON uc.co_fat_cidadao_pec  = c.co_fat_cidadao_pec
LEFT JOIN ultima_afericao_pressao up  ON up.co_fat_cidadao_pec  = c.co_fat_cidadao_pec
LEFT JOIN ultimo_peso_altura upa      ON upa.co_fat_cidadao_pec = c.co_fat_cidadao_pec;
