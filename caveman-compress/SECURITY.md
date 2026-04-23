# Segurança

## Classificação Snyk High Risk

`caveman-compress` recebe classificação Snyk High Risk devido a heurísticas de análise estática. Este documento explica o que a skill faz e o que não faz.

### O que dispara a classificação

1. **uso de subprocess**: A skill chama o CLI `claude` via `subprocess.run()` como fallback quando `ANTHROPIC_API_KEY` não está definida. A chamada de subprocess usa uma lista fixa de argumentos — nenhuma interpolação de shell acontece. Conteúdo do arquivo do usuário é passado via stdin, não como argumento de shell.

2. **Leitura/escrita de arquivo**: A skill lê o arquivo que o usuário explicitamente aponta, comprime, e escreve o resultado de volta no mesmo caminho. Um backup `.original.md` é salvo ao lado. Nenhum arquivo fora do caminho especificado pelo usuário é lido ou escrito.

### O que a skill NÃO faz

- Não executa conteúdo de arquivo do usuário como código
- Não faz requisições de rede exceto para a API da Anthropic (via SDK ou CLI)
- Não acessa arquivos fora do caminho fornecido pelo usuário
- Não usa shell=True nem interpolação de string em chamadas de subprocess
- Não coleta nem transmite dado algum além do arquivo sendo comprimido

### Comportamento de autenticação

Se `ANTHROPIC_API_KEY` estiver definida, a skill usa o SDK Python da Anthropic diretamente (sem subprocess). Se não, faz fallback para o CLI `claude`, que usa a autenticação existente do Claude desktop do usuário.

### Limite de tamanho de arquivo

Arquivos maiores que 500KB são rejeitados antes de qualquer chamada à API.

### Reportando uma vulnerabilidade

Se acredita ter encontrado uma questão de segurança genuína, por favor abra uma issue no GitHub com a label `security`.
