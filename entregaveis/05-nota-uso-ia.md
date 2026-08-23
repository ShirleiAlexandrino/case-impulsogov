# Nota sobre uso de IA

Usei o Claude (Claude Code) do início ao fim do case: leitura do enunciado e
dos arquivos de contexto, modelagem SQL das três camadas (bronze/silver/gold),
guardrails de qualidade por camada, tratamento de privacidade dos dados
(LGPD) e gestão de acesso, diagrama de arquitetura, documentação para o time
de produto e a mensagem para engenharia de dados.

**Diretrizes que dei.** Cinco decisões de arquitetura partiram de mim, não da
IA: a arquitetura medalhão (bronze/silver/gold) para o pipeline; os domínios
do TOGAF para estruturar o diagrama; o tratamento de privacidade dos dados
(LGPD, pela sensibilidade de dado de saúde); guardrails de qualidade por
camada; e, depois, um perfil gerencial adicional para diferenciar o acesso
por função.

**O que aceitei.** A execução da IA em cima dessas diretrizes — mas só depois
de validar: rodei o pipeline de verdade contra os três CSVs (não aceitei o
SQL de olho), conferindo contagens de linhas antes/depois da deduplicação,
casos específicos de pessoas (ex. reabertura de diagnóstico após "condição
resolvida") e os números finais da lista. Aceitei também a aplicação do
TOGAF, proporcional ao tamanho do case, sem inflar num processo ADM
completo; as camadas de minimização de dado (views por finalidade) e o
controle de acesso por perfil (`nu_ine`); e as assertions bloqueantes e
alertas informativos dos guardrails.

**O que rejeitei ou corrigi.** Duas coisas, em direções opostas:

1. O primeiro modelo da tabela final foi montado só a partir das regras de
   negócio escritas, sem comparar com o protótipo da tela aprovado pelo
   produto. Só percebi o problema quando perguntei diretamente "esse modelo
   atende a saída do protótipo?" — aí apareceram gaps reais: faltavam idade,
   o valor da aferição de pressão (o protótipo mostra "110/90 mmHg", não só a
   situação) e CPF como alternativa ao CNS. A IA não tinha comparado
   proativamente contra a imagem antes de propor o modelo; o problema não
   teria aparecido se eu não tivesse pedido essa checagem específica.
2. Cheguei a sugerir inferir a microárea (que falta nos dados brutos) a
   partir do DDD do telefone do cidadão. A IA verificou contra os dados reais
   — 1.200 telefones distintos para 1.200 pessoas, DDDs sem correlação nem
   dentro da mesma equipe de saúde — e me mostrou que a ideia não se
   sustentava. Descartei e documentei a ausência da microárea como limitação
   em vez de mascará-la.

**Exemplo concreto de erro.** O caso 1 acima: o modelo de dados inicial,
gerado com IA, não cobria todos os campos que a tela já aprovada exigia. Só
percebi comparando explicitamente contra o protótipo — lição prática de que
"a regra de negócio está implementada certo" e "o produto está atendido" são
verificações diferentes, e a segunda não acontece sozinha.
