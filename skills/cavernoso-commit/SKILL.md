---
name: cavernoso-commit
description: >
  Gerador de mensagens de commit ultracomprimidas. Corta ruído mantendo intenção e motivo.
  Formato Conventional Commits. Subject ≤50 chars, body só quando o "porquê" não está óbvio.
  Usar quando usuário disser "escreve um commit", "mensagem de commit", "gera commit",
  "/commit" ou invocar /cavernoso-commit. Ativa automaticamente ao fazer staging de mudanças.
---

Escrever mensagens de commit secas e exatas. Formato Conventional Commits. Sem enrolação. Porquê acima do quê.

## Regras

**Subject line:**
- `<type>(<scope>): <resumo no imperativo>` — `<scope>` opcional
- Types: `feat`, `fix`, `refactor`, `perf`, `docs`, `test`, `chore`, `build`, `ci`, `style`, `revert`
- Imperativo: "adicionar", "corrigir", "remover" — não "adicionado", "corrige", "corrigindo" (em formas não-imperativas)
- ≤50 chars quando possível, limite duro 72
- Sem ponto final
- Seguir convenção do projeto para capitalização depois dos dois-pontos

**Body (só se preciso):**
- Pular totalmente quando subject é autoexplicativo
- Adicionar body só pra: *porquê* não óbvio, breaking changes, notas de migração, issues vinculadas
- Quebrar linha em 72 chars
- Bullets `-` não `*`
- Referências a issues/PRs no fim: `Closes #42`, `Refs #17`

**O que NUNCA entra:**
- "Este commit faz X", "eu", "nós", "agora", "atualmente" — o diff diz o quê
- "Conforme solicitado por..." — usar trailer Co-authored-by
- "Gerado com Claude Code" ou qualquer atribuição a IA
- Emoji (a menos que convenção do projeto exija)
- Repetir nome do arquivo quando scope já diz

## Exemplos

Diff: endpoint novo pra perfil de usuário com body explicando o porquê
- ❌ "feat: adiciona um novo endpoint para buscar informações do perfil do usuário no banco"
- ✅
  ```
  feat(api): add GET /users/:id/profile

  Cliente mobile precisa de dados de perfil sem o payload completo
  de usuário para reduzir uso de LTE em cold-launch.

  Closes #128
  ```

Diff: mudança breaking de API
- ✅
  ```
  feat(api)!: rename /v1/orders to /v1/checkout

  BREAKING CHANGE: clientes em /v1/orders devem migrar para /v1/checkout
  antes de 2026-06-01. Rota antiga retorna 410 depois dessa data.
  ```

## Clareza automática

Sempre incluir body para: breaking changes, fixes de segurança, migrações de dados, qualquer coisa que reverta commit anterior. Nunca comprimir pra só subject — quem for debugar no futuro precisa do contexto.

## Limites

Só gera a mensagem. Não roda `git commit`, não faz staging, não amend. Saída como bloco de código pronto pra colar. "parar cavernoso-commit" ou "modo normal": volta ao estilo de commit verboso.
