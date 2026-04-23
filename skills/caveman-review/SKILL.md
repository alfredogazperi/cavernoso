---
name: caveman-review
description: >
  Comentários de review de código ultracomprimidos. Corta ruído de feedback em PR mantendo
  o sinal acionável. Cada comentário em uma linha: localização, problema, fix. Usar quando
  usuário disser "review esse PR", "code review", "revisa o diff", "/review" ou invocar
  /caveman-review. Ativa automaticamente ao revisar pull requests.
---

Escrever comentários de review secos e acionáveis. Uma linha por achado. Localização, problema, fix. Sem enrolação inicial.

## Regras

**Formato:** `L<linha>: <problema>. <fix>.` — ou `<arquivo>:L<linha>: ...` quando review é multi-arquivo.

**Prefixo de severidade (opcional, quando misto):**
- `🔴 bug:` — comportamento quebrado, vai causar incidente
- `🟡 risk:` — funciona mas frágil (race, falta null check, erro engolido)
- `🔵 nit:` — estilo, nome, micro-otimização. Autor pode ignorar
- `❓ q:` — pergunta genuína, não sugestão

**Cortar:**
- "Notei que...", "Parece que...", "Você poderia considerar..."
- "É só uma sugestão mas..." — usar `nit:`
- "Ótimo trabalho!", "No geral tá bom mas..." — dizer uma vez no topo, não por comentário
- Repetir o que a linha faz — o revisor lê o diff
- Hedging ("talvez", "pode ser", "acho que") — se incerto usa `q:`

**Manter:**
- Números de linha exatos
- Nomes exatos de símbolo/função/variável em crases
- Fix concreto, não "considerar refatorar isso"
- O *porquê* se o fix não for óbvio pelo problema

## Exemplos

❌ "Notei que na linha 42 você não está checando se o objeto user é nulo antes de acessar a propriedade email. Isso poderia causar um crash se o usuário não for encontrado no banco. Você pode querer adicionar um null check aqui."

✅ `L42: 🔴 bug: user pode ser null depois do .find(). Adicionar guard antes de .email.`

❌ "Parece que essa função faz muita coisa e talvez se beneficie de ser quebrada em funções menores pra legibilidade."

✅ `L88-140: 🔵 nit: fn de 50 linhas faz 4 coisas. Extrair validate/normalize/persist.`

❌ "Já pensou no que acontece se a API retornar 429? Acho que a gente deveria tratar esse caso."

✅ `L23: 🟡 risk: sem retry em 429. Envolver em withBackoff(3).`

## Clareza automática

Sair do modo seco para: achados de segurança (bugs classe CVE precisam de explicação completa + referência), desacordos arquiteturais (precisam de racional, não só uma linha), e contextos de onboarding em que o autor é novo e precisa do "porquê". Nesses casos, escrever parágrafo normal e depois voltar ao seco pro resto.

## Limites

Só review — não escreve o fix, não aprova / request-changes, não roda linters. Saída pronta pra colar no PR. "parar caveman-review" ou "modo normal": volta ao estilo de review verboso.
