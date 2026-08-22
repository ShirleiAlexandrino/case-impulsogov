# Nota sobre uso de IA

Usei o Claude (Claude Code) do início ao fim do case: leitura do enunciado e
dos arquivos de contexto, modelagem SQL das três camadas (bronze/silver/gold),
diagrama de arquitetura, documentação para o time de produto e a mensagem
para engenharia de dados.

**O que aceitei.** A estrutura de camadas e a lógica das regras de negócio —
mas só depois de rodar o pipeline de verdade contra os três CSVs (não aceitei
o SQL de olho): conferi contagens de linhas antes/depois da deduplicação,
casos específicos de pessoas (ex. reabertura de diagnóstico após "condição
resolvida"), e os números finais da lista. Também aceitei a sugestão de
estruturar o diagrama de arquitetura usando os domínios do TOGAF — pedi
explicitamente essa referência e a IA aplicou de forma proporcional ao
tamanho do case, sem inflar em um processo ADM completo.

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
