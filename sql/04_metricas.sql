-- ============================================================================
-- MÉTRICAS — números para o entregável 2 (ENTREGAVEIS.md)
-- ============================================================================

-- Total de pessoas na Lista Nominal de Hipertensão.
SELECT count(*) AS total_pessoas_na_lista
FROM gold_lista_nominal_hipertensao;

-- Distribuição de status por boa prática.
SELECT 'Consulta' AS boa_pratica, status_consulta AS status, count(*) AS pessoas
FROM gold_lista_nominal_hipertensao GROUP BY status_consulta
UNION ALL
SELECT 'Aferição de pressão', status_afericao_pressao, count(*)
FROM gold_lista_nominal_hipertensao GROUP BY status_afericao_pressao
UNION ALL
SELECT 'Peso e altura', status_peso_altura, count(*)
FROM gold_lista_nominal_hipertensao GROUP BY status_peso_altura
ORDER BY 1,
    CASE status
        WHEN 'EM DIA' THEN 1
        WHEN 'ATRASADA' THEN 2
        WHEN 'NUNCA REALIZADA' THEN 3
    END;
