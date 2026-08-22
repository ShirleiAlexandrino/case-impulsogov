-- ============================================================================
-- GUARDRAILS — validações automáticas por camada
--
-- Rodar depois que a camada correspondente tiver sido criada (bronze antes
-- dos guardrails de bronze, e assim por diante). Cada bloco "Guardrail"
-- interrompe a execução com error() se a condição de qualidade falhar — não
-- é um relatório, é um portão: se disparar, a camada seguinte não deveria
-- ser construída em cima do dado quebrado.
--
-- Os blocos "Alerta" não interrompem a execução. São para problemas que já
-- existem no dado de origem e a gente escolheu tratar (ver decisões em
-- sql/02_silver.sql e sql/03_gold.sql) ou reportar (ver
-- mensagem-engenharia-dados.md) em vez de bloquear a entrega.
-- ============================================================================


-- ============================== BRONZE =====================================

-- Guardrail B1 — nenhuma das três tabelas brutas pode chegar vazia.
SELECT error('bronze: cidadao_pec chegou vazio')
FROM (SELECT count(*) AS n FROM bronze_cidadao_pec) t WHERE n = 0;

SELECT error('bronze: atendimento_individual chegou vazio')
FROM (SELECT count(*) AS n FROM bronze_atendimento_individual) t WHERE n = 0;

SELECT error('bronze: procedimentos chegou vazio')
FROM (SELECT count(*) AS n FROM bronze_procedimentos) t WHERE n = 0;

-- Guardrail B2 — a chave primária declarada de cada tabela não pode ser nula.
SELECT error('bronze: co_fat_cidadao_pec nulo em cidadao_pec — ' || count(*) || ' linhas')
FROM bronze_cidadao_pec WHERE co_fat_cidadao_pec IS NULL HAVING count(*) > 0;

SELECT error('bronze: co_seq_fat_atd_ind nulo em atendimento_individual — ' || count(*) || ' linhas')
FROM bronze_atendimento_individual WHERE co_seq_fat_atd_ind IS NULL HAVING count(*) > 0;

SELECT error('bronze: co_seq_fat_proced nulo em procedimentos — ' || count(*) || ' linhas')
FROM bronze_procedimentos WHERE co_seq_fat_proced IS NULL HAVING count(*) > 0;


-- ============================== SILVER ======================================

-- Guardrail S1 — a deduplicação por chave deve produzir chave única. Se
-- disparar, a lógica de QUALIFY row_number() em sql/02_silver.sql quebrou.
SELECT error('silver: silver_cidadao com chave duplicada — ' || count(*) || ' chaves')
FROM (SELECT co_fat_cidadao_pec FROM silver_cidadao GROUP BY 1 HAVING count(*) > 1) t
HAVING count(*) > 0;

SELECT error('silver: silver_atendimento_individual com chave duplicada — ' || count(*) || ' chaves')
FROM (SELECT co_seq_fat_atd_ind FROM silver_atendimento_individual GROUP BY 1 HAVING count(*) > 1) t
HAVING count(*) > 0;

SELECT error('silver: silver_procedimentos com chave duplicada — ' || count(*) || ' chaves')
FROM (SELECT co_seq_fat_proced FROM silver_procedimentos GROUP BY 1 HAVING count(*) > 1) t
HAVING count(*) > 0;

-- Guardrail S2 — toda referência a cidadão em atendimento/procedimentos
-- precisa existir em silver_cidadao (sem órfãos).
SELECT error('silver: ' || count(*) || ' atendimentos referenciam cidadão inexistente')
FROM silver_atendimento_individual a
LEFT JOIN silver_cidadao c USING (co_fat_cidadao_pec)
WHERE c.co_fat_cidadao_pec IS NULL
HAVING count(*) > 0;

SELECT error('silver: ' || count(*) || ' procedimentos referenciam cidadão inexistente')
FROM silver_procedimentos p
LEFT JOIN silver_cidadao c USING (co_fat_cidadao_pec)
WHERE c.co_fat_cidadao_pec IS NULL
HAVING count(*) > 0;

-- Guardrail S3 — domínio fechado de classificação (contexto/02, seção 1).
SELECT error('silver: classificação fora do domínio esperado — ' || string_agg(DISTINCT atend_ind_classificacao, ', '))
FROM silver_atendimento_individual
WHERE atend_ind_classificacao NOT IN
    ('GERAL', 'HIPERTENSÃO', 'HIPERTENSÃO - CONDIÇÃO RESOLVIDA', 'DIABETES')
HAVING count(*) > 0;

-- Guardrail S4 — domínio fechado de procedimento (contexto/03).
SELECT error('silver: ds_proced fora do domínio esperado — ' || string_agg(DISTINCT ds_proced, ', '))
FROM silver_procedimentos
WHERE ds_proced NOT IN ('AFERIÇÃO DE PRESSÃO ARTERIAL', 'MEDIÇÃO PESO E ALTURA')
HAVING count(*) > 0;

-- Alerta S5 — registro com data posterior à data de referência do retrato
-- (2026-08-01). Não bloqueia porque não impede o cálculo dos status (uma
-- data futura só faz a pessoa parecer "em dia" incorretamente) — mas é
-- sintoma de erro de digitação/registro na origem. Ver mensagem-engenharia-
-- -dados.md.
SELECT 'ALERTA silver: ' || count(*) || ' atendimentos com dt_registro após 2026-08-01' AS aviso
FROM silver_atendimento_individual WHERE dt_registro > DATE '2026-08-01'
HAVING count(*) > 0;

SELECT 'ALERTA silver: ' || count(*) || ' procedimentos com dt_registro após 2026-08-01' AS aviso
FROM silver_procedimentos WHERE dt_registro > DATE '2026-08-01'
HAVING count(*) > 0;

-- Alerta S6 — data de nascimento implausível (futura, ou idade > 120 anos).
SELECT 'ALERTA silver: ' || count(*) || ' cidadãos com data de nascimento implausível' AS aviso
FROM silver_cidadao
WHERE dt_registro_nascimento > DATE '2026-08-01'
   OR date_part('year', age(DATE '2026-08-01', dt_registro_nascimento)) > 120
HAVING count(*) > 0;

-- Alerta S7 — no_equipe é texto livre; nu_ine é a chave estável da equipe
-- (contexto/01-lista-nominal.md). Já achamos dois nu_ine gravados com o
-- mesmo no_equipe ("ESF 5") — qualquer agrupamento por nome, em vez de
-- código, mistura equipes reais numa só. Este alerta existe pra pegar
-- automaticamente se isso mudar ou se acontecer de novo com outro nome:
-- nenhuma consulta/relatório deste projeto deve agrupar por no_equipe.
SELECT 'ALERTA silver: ' || count(*) || ' no_equipe associados a mais de um nu_ine — agrupar sempre por nu_ine' AS aviso
FROM (
    SELECT no_equipe
    FROM silver_cidadao
    GROUP BY no_equipe
    HAVING count(DISTINCT nu_ine) > 1
) t
HAVING count(*) > 0;


-- ================================ GOLD ======================================

-- Guardrail G1 — granularidade da tabela final: 1 linha por cidadão.
SELECT error('gold: PK duplicada — ' || count(*) || ' cidadãos com mais de uma linha')
FROM (SELECT co_fat_cidadao_pec FROM gold_lista_nominal_hipertensao GROUP BY 1 HAVING count(*) > 1) t
HAVING count(*) > 0;

-- Guardrail G2 — critério de saída "faleceu" não pode falhar: ninguém
-- marcado como falecido pode aparecer na lista.
SELECT error('gold: ' || count(*) || ' pessoas falecidas na lista')
FROM gold_lista_nominal_hipertensao g
JOIN silver_cidadao c USING (co_fat_cidadao_pec)
WHERE c.faleceu
HAVING count(*) > 0;

-- Guardrail G3 — os três status só assumem os valores definidos na regra de
-- negócio (contexto/02, seção 3).
SELECT error('gold: status_consulta com valor fora do domínio')
FROM gold_lista_nominal_hipertensao
WHERE status_consulta NOT IN ('EM DIA', 'ATRASADA', 'NUNCA REALIZADA')
HAVING count(*) > 0;

SELECT error('gold: status_afericao_pressao com valor fora do domínio')
FROM gold_lista_nominal_hipertensao
WHERE status_afericao_pressao NOT IN ('EM DIA', 'ATRASADA', 'NUNCA REALIZADA')
HAVING count(*) > 0;

SELECT error('gold: status_peso_altura com valor fora do domínio')
FROM gold_lista_nominal_hipertensao
WHERE status_peso_altura NOT IN ('EM DIA', 'ATRASADA', 'NUNCA REALIZADA')
HAVING count(*) > 0;

-- Guardrail G4 — invariante estrutural documentado em documentacao-
-- -produto.md: "Consulta" nunca pode ser "Nunca realizada", porque o
-- critério de entrada na lista já exige uma consulta com médico/enfermeiro.
-- Se isso disparar, a regra de entrada e a regra de "Consulta" divergiram.
SELECT error('gold: ' || count(*) || ' pessoas com status_consulta = NUNCA REALIZADA (viola regra de entrada)')
FROM gold_lista_nominal_hipertensao
WHERE status_consulta = 'NUNCA REALIZADA'
HAVING count(*) > 0;

-- Alerta G5 — idade fora de faixa plausível. Mesma causa raiz do alerta S6;
-- reportado aqui de novo porque é o campo que chega até a tela.
SELECT 'ALERTA gold: ' || count(*) || ' pessoas na lista com idade fora da faixa 0-110' AS aviso
FROM gold_lista_nominal_hipertensao
WHERE idade < 0 OR idade > 110
HAVING count(*) > 0;


-- ========================= PRIVACIDADE / LGPD ===============================

-- Guardrail P1 — a view analítica não pode expor identificador direto. Se
-- alguém adicionar nome/CPF/CNS/telefone/PK a essa view no futuro, isso
-- quebra a minimização de dados descrita em lgpd-notas.md.
SELECT error('lgpd: view analítica expõe identificador — ' || string_agg(column_name, ', '))
FROM information_schema.columns
WHERE table_name = 'gold_lista_nominal_hipertensao_analitico'
  AND column_name IN ('co_fat_cidadao_pec', 'no_cidadao', 'nu_cpf_cidadao', 'nu_cns', 'nu_telefone_celular')
HAVING count(*) > 0;

-- Guardrail P2 — a view mascarada não pode conter telefone (suporte/QA não
-- precisa contatar ninguém), e o mascaramento de CPF/CNS precisa seguir o
-- padrão esperado (não pode vazar o documento completo).
SELECT error('lgpd: view mascarada expõe telefone — não deveria estar presente')
FROM information_schema.columns
WHERE table_name = 'gold_lista_nominal_hipertensao_mascarado'
  AND column_name = 'nu_telefone_celular'
HAVING count(*) > 0;

SELECT error('lgpd: ' || count(*) || ' CPFs mascarados fora do padrão esperado')
FROM gold_lista_nominal_hipertensao_mascarado
WHERE nu_cpf_mascarado NOT LIKE '***.***.***-__'
HAVING count(*) > 0;

SELECT error('lgpd: ' || count(*) || ' CNS mascarados fora do padrão esperado')
FROM gold_lista_nominal_hipertensao_mascarado
WHERE nu_cns_mascarado NOT LIKE '***********____'
HAVING count(*) > 0;
