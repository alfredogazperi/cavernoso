---
name: cavernoso-compress
description: >
  Comprimir arquivos de memória em linguagem natural (CLAUDE.md, todos, preferências) para
  o formato cavernoso e economizar tokens de input. Preserva toda substância técnica,
  código, URLs e estrutura. A versão comprimida sobrescreve o original.
  Backup legível salvo como ARQUIVO.original.md. Otimizado para pt-BR.
  Trigger: /cavernoso:compress <caminho> ou "comprimir arquivo de memória"
---

# Cavernoso Compress (pt-BR)

## Propósito

Comprimir arquivos em linguagem natural (CLAUDE.md, todos, preferências) para fala cavernosa pt-BR e reduzir tokens de input. Versão comprimida sobrescreve o original. Backup legível salvo como `<arquivo>.original.md`.

## Trigger

`/cavernoso:compress <caminho>` ou quando usuário pede pra comprimir um arquivo de memória.

## Processo

1. Scripts de compressão vivem em `skills/cavernoso-compress/scripts/` (ao lado deste SKILL.md). Se o caminho não estiver disponível, procurar `scripts/__main__.py`.

2. Rodar:

cd skills/cavernoso-compress && python3 -m scripts <caminho_absoluto>

3. O CLI vai:
- detectar tipo de arquivo (sem tokens)
- chamar Claude pra comprimir
- validar saída (sem tokens)
- se erro: cherry-pick fix com Claude (correções alvo, sem recomprimir)
- retry até 2 vezes
- se falhar depois de 2 retries: reportar erro, deixar arquivo original intocado

4. Retornar resultado pro usuário

## Regras de Compressão

### Remover

- Artigos: o, a, os, as, um, uma, uns, umas
- Filler: basicamente, simplesmente, na verdade, efetivamente, literalmente, realmente, praticamente, obviamente, claramente, meio que, tipo, então (filler), enfim
- Cortesias: "com certeza", "claro", "sem dúvida", "fico feliz em", "recomendo que", "sugiro que"
- Hedging: "talvez seja interessante", "vale a pena considerar", "seria bom", "pode ser que", "eu acho que"
- Redundâncias: "de forma a" → "para", "no sentido de" → "para", "pelo fato de que" → "porque", "tendo em vista que" → "pois", "em virtude de" → "por"
- Fluff conectivo: "além disso", "ademais", "entretanto", "todavia", "outrossim", "dessa forma", "sendo assim", "nesse sentido", "dito isso"

### Preservar EXATO (nunca modificar)

- Blocos de código (``` cercados e indentados)
- Código inline (`conteúdo em crase`)
- URLs e links (URLs completas, links markdown)
- Caminhos de arquivo (`/src/components/...`, `./config.yaml`)
- Comandos (`npm install`, `git commit`, `docker build`)
- Termos técnicos (nomes de libs, APIs, protocolos, algoritmos)
- Nomes próprios (projetos, pessoas, empresas)
- Datas, números de versão, valores numéricos
- Variáveis de ambiente (`$HOME`, `NODE_ENV`)
- **Termos técnicos em inglês estabelecidos:** push, pull, commit, merge, deploy, build, release, rollback, feature, branch, tag, issue, PR, runtime, stack, framework, endpoint, payload, request, response, bug, fix, hook, trigger, callback, pipeline

### Preservar estrutura

- Todos cabeçalhos markdown (manter texto exato, comprimir corpo abaixo)
- Hierarquia de bullets (manter nível de indentação)
- Listas numeradas (manter numeração)
- Tabelas (comprimir texto de célula, manter estrutura)
- Frontmatter / cabeçalhos YAML em arquivos markdown

### Comprimir

- Usar sinônimos curtos: "usar" não "utilizar", "ver" não "visualizar", "fazer" não "realizar", "achar" não "encontrar", "grande" não "extenso", "fix" não "implementar uma solução para"
- Fragmentos OK: "Rodar testes antes do commit" não "Você deve sempre rodar os testes antes de fazer o commit"
- Cortar "você deve", "certifique-se de", "lembre-se de" — só afirmar a ação
- Fundir bullets redundantes que dizem a mesma coisa de formas diferentes
- Manter um exemplo quando múltiplos mostram o mesmo padrão

REGRA CRÍTICA:
Qualquer coisa dentro de ``` ... ``` deve ser copiada EXATAMENTE.
Não:
- remover comentários
- remover espaços
- reordenar linhas
- encurtar comandos
- simplificar nada

Código inline (`...`) deve ser preservado EXATO.
Não modificar nada entre crases.

Se o arquivo contém blocos de código:
- Tratar blocos como regiões read-only
- Comprimir só texto fora deles
- Não fundir seções ao redor do código

IDIOMA:
Saída DEVE permanecer em português. Não traduzir para inglês.

## Padrão

Original:
> Você deve sempre se certificar de rodar a suíte de testes antes de fazer push de qualquer mudança para a branch main. Isso é importante porque ajuda a pegar bugs cedo e previne builds quebrados em produção.

Comprimido:
> Rodar testes antes de push para main. Pega bugs cedo, previne prod quebrada.

Original:
> A aplicação usa uma arquitetura de microsserviços com os seguintes componentes. O API gateway trata todas as requisições recebidas e as roteia para o serviço apropriado. O serviço de autenticação é responsável por gerenciar sessões de usuário e tokens JWT.

Comprimido:
> Arquitetura microsserviços. API gateway roteia requisições para serviços. Auth service gerencia sessões de usuário + tokens JWT.

Original:
> É importante notar que o processo de deploy deve ser feito sempre após a validação completa dos testes de integração, pois caso contrário podemos ter problemas em produção.

Comprimido:
> Deploy só depois de testes de integração validados. Senão quebra prod.

## Limites

- SÓ comprimir arquivos em linguagem natural (.md, .txt, sem extensão)
- NUNCA modificar: .py, .js, .ts, .json, .yaml, .yml, .toml, .env, .lock, .css, .html, .xml, .sql, .sh
- Se arquivo tem conteúdo misto (prosa + código), comprimir SÓ a prosa
- Se incerto se algo é código ou prosa, deixar intocado
- Arquivo original salvo como FILE.original.md antes de sobrescrever
- Nunca comprimir FILE.original.md (pular)
