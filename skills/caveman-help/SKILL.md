---
name: caveman-help
description: >
  Cartão de referência rápida pra todos os modos, skills e comandos cavernosos.
  Display one-shot, não é modo persistente. Trigger: /caveman-help,
  "ajuda cavernoso", "quais comandos cavernoso", "como uso cavernoso".
---

# Ajuda Cavernoso

Mostrar este cartão de referência quando invocado. One-shot — NÃO muda modo, não escreve flag, não persiste nada. Saída em estilo cavernoso.

## Modos

| Modo | Trigger | O que muda |
|------|---------|-----------|
| **Lite** | `/caveman lite` | Corta filler. Mantém estrutura de frase. |
| **Full** | `/caveman` | Corta artigos, filler, cortesias, hedging. Fragmentos OK. Padrão. |
| **Ultra** | `/caveman ultra` | Compressão extrema. Fragmentos nus. Tabelas acima de prosa. |

Modo persiste até mudar ou fim da sessão.

## Skills

| Skill | Trigger | O que faz |
|-------|---------|-----------|
| **caveman-commit** | `/caveman-commit` | Mensagens de commit secas. Conventional Commits. Subject ≤50 chars. |
| **caveman-review** | `/caveman-review` | Comentários de PR de uma linha: `L42: bug: user null. Add guard.` |
| **caveman-compress** | `/caveman:compress <arquivo>` | Comprime .md pra prosa cavernosa pt-BR. Economiza ~35% tokens. |
| **caveman-help** | `/caveman-help` | Este cartão. |

## Desativar

Dizer "parar cavernoso" ou "modo normal". Voltar a qualquer momento com `/caveman`.

## Configurar modo padrão

Modo padrão = `full`. Mudar:

**Variável de ambiente** (prioridade máxima):
```bash
export CAVEMAN_DEFAULT_MODE=ultra
```

**Arquivo de config** (`~/.config/caveman/config.json`):
```json
{ "defaultMode": "lite" }
```

Colocar `"off"` pra desabilitar ativação automática no início da sessão. Usuário ainda ativa manualmente com `/caveman`.

Resolução: env var > arquivo de config > `full`.

## Mais

Docs completos: https://github.com/alfredogazperi/cavernoso
