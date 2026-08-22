-- ============================================================================
-- CAMADA BRONZE — ingestão bruta, sem lógica de negócio
-- Fonte: dados/*.csv (extração e-SUS PEC, retrato em 2026-08-01)
--
-- Como rodar (a partir da raiz do repositório, com duckdb CLI):
--   duckdb case_impulso.duckdb
--   .read sql/01_bronze.sql
--   .read sql/02_silver.sql
--   .read sql/03_gold.sql
--   .read sql/04_metricas.sql
--
-- Tipagem explícita conforme contexto/03-dicionario-dados.md, para evitar que
-- o auto-detect de CSV promova códigos numéricos com zero à esquerda
-- (nu_ine, nu_cbo, nu_cns, nu_cpf...) para tipos numéricos e corrompa o valor.
--
-- Desvio do dicionário: co_seq_fat_atd_ind é documentado como bigint, mas os
-- valores reais são compostos (ex.: "4100001.HIPERTENSÃO" — id + linha de
-- cuidado). Tratado aqui como VARCHAR; ver mensagem ao time de dados.
-- ============================================================================

CREATE OR REPLACE TABLE bronze_cidadao_pec AS
SELECT * FROM read_csv('dados/cidadao_pec.csv',
    header = true,
    columns = {
        'co_fat_cidadao_pec':               'BIGINT',
        'no_cidadao':                       'VARCHAR',
        'dt_registro_nascimento':           'DATE',
        'ds_sexo':                          'VARCHAR',
        'nu_cns':                           'VARCHAR',
        'nu_cpf_cidadao':                   'VARCHAR',
        'nu_telefone_celular':              'VARCHAR',
        'st_faleceu':                       'SMALLINT',
        'dt_ultima_atualizacao_cidadao':    'TIMESTAMP',
        'st_diabetes_diagnosticada':        'SMALLINT',
        'st_hipertensao_diagnosticada':     'SMALLINT',
        'nu_ine':                           'VARCHAR',
        'no_equipe':                        'VARCHAR',
        'data_ultimo_atend_individual':     'DATE',
        'equipe_ine_atendimento':           'VARCHAR',
        'equipe_nome_atendimento':          'VARCHAR',
        'nu_atend_ubs_ultimos_12_meses':    'BIGINT',
        'data_transmissao':                 'DATE'
    }
);

CREATE OR REPLACE TABLE bronze_atendimento_individual AS
SELECT * FROM read_csv('dados/atendimento_individual.csv',
    header = true,
    columns = {
        'co_seq_fat_atd_ind':      'VARCHAR',  -- ver nota de desvio acima
        'co_fat_cidadao_pec':      'BIGINT',
        'atend_ind_classificacao': 'VARCHAR',
        'nu_ciap':                 'VARCHAR',
        'no_ciap':                 'VARCHAR',
        'nu_cid':                  'VARCHAR',
        'no_cid':                  'VARCHAR',
        'no_profissional':         'VARCHAR',
        'nu_cbo':                  'VARCHAR',
        'no_cbo':                  'VARCHAR',
        'ds_local_atendimento':    'VARCHAR',
        'nu_ine':                  'VARCHAR',
        'no_equipe':               'VARCHAR',
        'dt_registro':             'DATE',
        'data_transmissao':        'DATE',
        'propriedades':            'VARCHAR',
        'versao':                  'VARCHAR'
    }
);

CREATE OR REPLACE TABLE bronze_procedimentos AS
SELECT * FROM read_csv('dados/procedimentos.csv',
    header = true,
    columns = {
        'tabela':                        'VARCHAR',
        'co_seq_fat_proced':              'VARCHAR',
        'co_fat_cidadao_pec':             'BIGINT',
        'co_proced':                      'VARCHAR',
        'ds_proced':                      'VARCHAR',
        'nu_ine':                         'VARCHAR',
        'no_equipe':                      'VARCHAR',
        'no_profissional':                'VARCHAR',
        'nu_cbo':                         'VARCHAR',
        'no_cbo':                         'VARCHAR',
        'dt_registro':                    'DATE',
        'qt_afericao_pressao_arterial':   'VARCHAR',
        'qt_glicemia':                    'VARCHAR',
        'data_transmissao':               'DATE',
        'propriedades':                   'VARCHAR',
        'versao':                         'VARCHAR'
    }
);
