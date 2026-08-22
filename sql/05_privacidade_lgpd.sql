-- ============================================================================
-- CAMADA DE PRIVACIDADE — LGPD (Lei 13.709/2018)
--
-- `gold_lista_nominal_hipertensao` contém dado pessoal sensível (condição de
-- saúde — art. 5º, II) e identificadores diretos (nome, CPF, CNS, telefone).
-- Ela permanece com exposição completa porque essa é a finalidade que
-- justifica o tratamento: a equipe de saúde precisa localizar e contatar a
-- pessoa (base legal — art. 11, II, "f": tutela da saúde, em procedimento
-- realizado por profissionais/serviços de saúde).
--
-- Qualquer consumo com finalidade diferente (gestão agregada, suporte, QA)
-- não tem a mesma justificativa para ver identificador completo. As views
-- abaixo aplicam minimização de dados (art. 6º, III) por camada de acesso —
-- ver contexto e recomendações em lgpd-notas.md.
-- ============================================================================

-- Uso analítico/gerencial (dashboards agregados, relatórios de cobertura).
-- Sem nome, documento ou telefone — não é necessário para medir a saúde do
-- programa, só para agir sobre uma pessoa específica.
CREATE OR REPLACE VIEW gold_lista_nominal_hipertensao_analitico AS
SELECT
    nu_ine,
    no_equipe,
    CASE
        WHEN idade < 18 THEN '0-17'
        WHEN idade < 30 THEN '18-29'
        WHEN idade < 45 THEN '30-44'
        WHEN idade < 60 THEN '45-59'
        WHEN idade < 75 THEN '60-74'
        ELSE '75+'
    END AS faixa_etaria,
    status_consulta,
    status_afericao_pressao,
    status_peso_altura
FROM gold_lista_nominal_hipertensao;

-- Uso de suporte/QA — precisa localizar um registro específico para
-- investigar um caso, mas não precisa (nem deve) reter o documento
-- completo da pessoa. Mantém nome (para conferência humana) e mascara
-- CPF/CNS, mostrando só os dígitos finais. Sem telefone: suporte/QA não
-- liga para o cidadão.
CREATE OR REPLACE VIEW gold_lista_nominal_hipertensao_mascarado AS
SELECT
    co_fat_cidadao_pec,
    no_cidadao,
    '***.***.***-' || right(nu_cpf_cidadao, 2) AS nu_cpf_mascarado,
    '***********' || right(nu_cns, 4)          AS nu_cns_mascarado,
    idade,
    nu_ine,
    no_equipe,
    status_consulta,
    status_afericao_pressao,
    status_peso_altura
FROM gold_lista_nominal_hipertensao;
