---
name: cavernoso-help
description: >
  Cartão de referência rápida pra todos os modos, skills e comandos cavernosos.
  Display one-shot, não é modo persistente. Trigger: /cavernoso-help,
  "ajuda cavernoso", "quais comandos cavernoso", "como uso cavernoso".
---

# Ajuda Cavernoso

Mostrar este cartão de referência quando invocado. One-shot — NÃO muda modo, não escreve flag, não persiste nada. Saída em estilo cavernoso.

## Modos

| Modo | Trigger | O que muda |
|------|---------|-----------|
| **Leve** | `/cavernoso leve` | Corta filler. Mantém estrutura de frase. |
| **Total** | `/cavernoso` | Corta artigos, filler, cortesias, hedging. Fragmentos OK. Padrão. |
| **Ultra** | `/cavernoso ultra` | Compressão extrema. Fragmentos nus. Tabelas acima de prosa. |

Modo persiste até mudar ou fim da sessão.

## Skills

| Skill | Trigger | O que faz |
|-------|---------|-----------|
| **cavernoso-commit** | `/cavernoso-commit` | Mensagens de commit secas. Conventional Commits. Subject ≤50 chars. |
| **cavernoso-review** | `/cavernoso-review` | Comentários de PR de uma linha: `L42: bug: user null. Add guard.` |
| **cavernoso-compress** | `/cavernoso:compress <arquivo>` | Comprime .md pra prosa cavernosa pt-BR. Economiza ~35% tokens. |
| **cavernoso-help** | `/cavernoso-help` | Este cartão. |

## Desativar

Dizer "parar cavernoso" ou "modo normal". Voltar a qualquer momento com `/cavernoso`.

## Configurar modo padrão

Modo padrão = `total`. Mudar:

**Variável de ambiente** (prioridade máxima):
```bash
export CAVEMAN_DEFAULT_MODE=ultra
```

**Arquivo de config** (`~/.config/caveman/config.json`):
```json
{ "defaultMode": "leve" }
```

Colocar `"off"` pra desabilitar ativação automática no início da sessão. Usuário ainda ativa manualmente com `/cavernoso`.

Resolução: env var > arquivo de config > `total`.

## Mais

Docs completos: https://github.com/alfredogazperi/cavernoso
