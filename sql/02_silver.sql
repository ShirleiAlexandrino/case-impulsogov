-- ============================================================================
-- CAMADA SILVER — deduplicação, limpeza, padronização
--
-- O dicionário de dados descreve cargas incrementais mensais que reenviam
-- registros já existentes (confirmado nos dados: mesmas chaves aparecem em
-- transmissões diferentes, às vezes com pequenas divergências de texto, ex.
-- "ESF 2" vs "Esf 2"). Em todas as três tabelas, mantemos 1 linha por chave,
-- a da transmissão mais recente.
-- ============================================================================

CREATE OR REPLACE TABLE silver_cidadao AS
SELECT
    co_fat_cidadao_pec,
    trim(no_cidadao)          AS no_cidadao,
    dt_registro_nascimento,
    ds_sexo,
    nu_cns,
    nu_cpf_cidadao,
    nu_telefone_celular,
    st_faleceu = 1             AS faleceu,
    nu_ine,
    -- no_equipe é texto livre digitado no sistema, nu_ine é a chave estável
    -- (contexto/01-lista-nominal.md). Existem dois nu_ine gravados com o
    -- mesmo no_equipe ("ESF 5") na base — nunca agrupar/comparar equipes por
    -- no_equipe, só por nu_ine. Ver guardrail S7 em sql/06_guardrails.sql.
    trim(no_equipe)            AS no_equipe,
    data_transmissao
FROM bronze_cidadao_pec
-- Nota: não existe campo de microárea em nenhuma das três tabelas brutas.
-- O protótipo da tela pede esse recorte (coluna "Território", filtro
-- "Microárea"); decidimos não inferi-lo a partir de nu_telefone_celular
-- (DDD é código de telefonia, sem relação com território sanitário — não há
-- correlação nem mesmo dentro da mesma equipe nos dados reais). Ver
-- limitação documentada em diagrama-arquitetura.md.
QUALIFY row_number() OVER (
    PARTITION BY co_fat_cidadao_pec
    ORDER BY data_transmissao DESC
) = 1;

CREATE OR REPLACE TABLE silver_atendimento_individual AS
SELECT
    co_seq_fat_atd_ind,
    co_fat_cidadao_pec,
    atend_ind_classificacao,
    no_profissional,
    nu_cbo,
    left(nu_cbo, 4)            AS cbo_familia,
    dt_registro,
    data_transmissao
FROM bronze_atendimento_individual
QUALIFY row_number() OVER (
    PARTITION BY co_seq_fat_atd_ind
    ORDER BY data_transmissao DESC
) = 1;

CREATE OR REPLACE TABLE silver_procedimentos AS
SELECT
    co_seq_fat_proced,
    co_fat_cidadao_pec,
    ds_proced,
    no_profissional,
    nu_cbo,
    left(nu_cbo, 4)                                                  AS cbo_familia,
    dt_registro,
    try_cast(json_extract_string(propriedades, '$.peso')   AS DOUBLE) AS peso_kg,
    try_cast(json_extract_string(propriedades, '$.altura') AS DOUBLE) AS altura_cm,
    json_extract_string(propriedades, '$.pressao_arterial')           AS pressao_arterial,
    data_transmissao
FROM bronze_procedimentos
QUALIFY row_number() OVER (
    PARTITION BY co_seq_fat_proced
    ORDER BY data_transmissao DESC
) = 1;
