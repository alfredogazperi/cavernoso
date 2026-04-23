# CLAUDE.md — caveman

## README é artefato de produto

README = porta de entrada do produto. Pessoas não-técnicas leem pra decidir se caveman vale o install. Trate como copy de UI.

**Regras para qualquer mudança de README:**

- Legível por usuários não-agentes-de-IA. Se você escrever "hook SessionStart injeta contexto de sistema", invisível pra maioria — traduza.
- Mantenha exemplos Antes/Depois primeiro. Isso é o pitch.
- Tabela de instalação sempre completa + acurada. Um comando de install quebrado custa usuário real.
- Tabela "What You Get" precisa sincronizar com o código real. Feature entra ou sai → atualize a tabela.
- Preserve a voz. Caveman fala no README de propósito. "Brain still big." "Cost go down forever." "One rock. That it." — brand intencional. Não normalize.
- Números de benchmark vêm de rodadas reais em `benchmarks/` e `evals/`. Nunca invente nem arredonde. Rode de novo se tiver dúvida.
- Adicionando agente novo à tabela de install → adicione bloco de detalhes na seção `<details>` abaixo.
- Checagem de legibilidade antes de qualquer commit de README: um não-programador entenderia + instalaria em 60 segundos?

---

## Visão geral do projeto

Caveman faz agentes de IA de código responderem em prosa estilo caveman comprimida — corta ~65-75% dos tokens de saída, precisão técnica completa. Distribuído como plugin do Claude Code, plugin do Codex, extensão do Gemini CLI, arquivos de rule de agente para Cursor, Windsurf, Cline, Copilot, 40+ outros via `npx skills`.

---

## Estrutura de arquivos e quem é dono do quê

### Arquivos fonte única da verdade — edite só estes

| Arquivo | O que controla |
|------|-----------------|
| `skills/caveman/SKILL.md` | Comportamento do caveman: níveis de intensidade, regras, auto-clareza, persistência. Único arquivo a editar para mudanças de comportamento. |
| `rules/caveman-activate.md` | Corpo da regra de auto-ativação always-on. CI injeta nos arquivos de rule de Cursor, Windsurf, Cline, Copilot. Edite aqui, não nas cópias específicas por agente. |
| `skills/caveman-commit/SKILL.md` | Comportamento de mensagem de commit do caveman. Skill totalmente independente. |
| `skills/caveman-review/SKILL.md` | Comportamento de code review do caveman. Skill totalmente independente. |
| `skills/caveman-help/SKILL.md` | Cartão de referência rápida. Display one-shot, não um modo persistente. |
| `caveman-compress/SKILL.md` | Comportamento da sub-skill compress. |

### Auto-gerado / auto-sincronizado — não edite diretamente

Sobrescritos pelo CI no push para main quando as fontes mudam. Edições aqui são perdidas.

| Arquivo | Sincronizado de |
|------|-------------|
| `caveman/SKILL.md` | `skills/caveman/SKILL.md` |
| `plugins/caveman/skills/caveman/SKILL.md` | `skills/caveman/SKILL.md` |
| `.cursor/skills/caveman/SKILL.md` | `skills/caveman/SKILL.md` |
| `.windsurf/skills/caveman/SKILL.md` | `skills/caveman/SKILL.md` |
| `caveman.skill` | ZIP do diretório `skills/caveman/` |
| `.clinerules/caveman.md` | `rules/caveman-activate.md` |
| `.github/copilot-instructions.md` | `rules/caveman-activate.md` |
| `.cursor/rules/caveman.mdc` | `rules/caveman-activate.md` + frontmatter do Cursor |
| `.windsurf/rules/caveman.md` | `rules/caveman-activate.md` + frontmatter do Windsurf |

---

## Workflow de sync do CI

`.github/workflows/sync-skill.yml` dispara no push para main quando `skills/caveman/SKILL.md` ou `rules/caveman-activate.md` muda.

O que faz:
1. Copia `skills/caveman/SKILL.md` para todos os locais de SKILL.md específicos por agente
2. Reconstrói `caveman.skill` como ZIP de `skills/caveman/`
3. Reconstrói todos os arquivos de rule de agente a partir de `rules/caveman-activate.md`, prependendo frontmatter específico por agente (Cursor precisa de `alwaysApply: true`, Windsurf precisa de `trigger: always_on`)
4. Faz commit e push com `[skip ci]` para evitar loops

Bot do CI commita como `github-actions[bot]`. Após merge do PR, espere o workflow antes de declarar release completa.

---

## Sistema de hooks (Claude Code)

Três hooks em `hooks/` mais um módulo compartilhado `caveman-config.js` e um marker `package.json` CommonJS. Comunicam via arquivo de flag em `$CLAUDE_CONFIG_DIR/.caveman-active` (cai para `~/.claude/.caveman-active`).

```
SessionStart hook ──writes "full"──▶ $CLAUDE_CONFIG_DIR/.caveman-active ◀──writes mode── UserPromptSubmit hook
                                                       │
                                                    reads
                                                       ▼
                                              caveman-statusline.sh
                                            [CAVEMAN] / [CAVEMAN:ULTRA] / ...
```

`hooks/package.json` fixa o diretório em `{"type": "commonjs"}` para que os hooks `.js` resolvam como CJS mesmo quando um `package.json` ancestral (ex.: `~/.claude/package.json` de outro plugin) declara `"type": "module"`. Sem isso, `require()` explode com `ReferenceError: require is not defined in ES module scope`.

Todos os hooks honram `CLAUDE_CONFIG_DIR` para locais de config do Claude Code não-padrão.

### `hooks/caveman-config.js` — módulo compartilhado

Exporta:
- `getDefaultMode()` — resolve modo padrão a partir da env var `CAVEMAN_DEFAULT_MODE`, depois `$XDG_CONFIG_HOME/caveman/config.json` / `~/.config/caveman/config.json` / `%APPDATA%\caveman\config.json`, depois `'full'`
- `safeWriteFlag(flagPath, content)` — escrita de flag segura contra symlink. Recusa se o alvo da flag ou seu pai imediato for symlink. Abre com `O_NOFOLLOW` onde suportado. Temp atômico + rename. Cria com `0600`. Protege contra atacantes locais substituindo o caminho de flag previsível por um symlink pra sobrescrever arquivos graváveis pelo usuário. Usado pelos dois hooks de escrita. Falha silenciosa em todos erros de filesystem.

### `hooks/caveman-activate.js` — hook SessionStart

Roda uma vez por início de sessão do Claude Code. Três coisas:
1. Escreve o modo ativo em `$CLAUDE_CONFIG_DIR/.caveman-active` via `safeWriteFlag` (cria se ausente)
2. Emite o ruleset do caveman como stdout oculto — Claude Code injeta stdout do hook SessionStart como contexto de sistema, invisível ao usuário
3. Checa `settings.json` para config de statusline; se ausente, anexa cutucada pra oferecer setup na primeira interação

Falha silenciosa em todos erros de filesystem — nunca bloqueia o início da sessão.

### `hooks/caveman-mode-tracker.js` — hook UserPromptSubmit

Lê JSON do stdin. Três responsabilidades:

**1. Ativação por slash-command.** Se o prompt começa com `/caveman`, escreve modo no arquivo de flag via `safeWriteFlag`:
- `/caveman` → padrão configurado (veja `caveman-config.js`, default `full`)
- `/caveman lite` → `lite`
- `/caveman ultra` → `ultra`
- `/caveman-commit` → `commit`
- `/caveman-review` → `review`
- `/caveman-compress` → `compress`

**2. Ativação/desativação por linguagem natural.** Casa frases como "activate caveman", "turn on caveman mode", "talk like caveman" e escreve o modo padrão configurado. Casa "stop caveman", "disable caveman", "normal mode", "deactivate caveman" etc. e deleta o arquivo de flag. README promete esses triggers, o hook executa.

**3. Reforço por turno.** Quando a flag está setada para um modo não-independente (ou seja, não `commit`/`review`/`compress`), emite um pequeno reminder JSON `hookSpecificOutput` pro modelo manter o estilo caveman depois que outros plugins injetam instruções competindo no meio da conversa. O ruleset completo ainda vem do SessionStart — isto é só uma âncora de atenção.

### `hooks/caveman-statusline.sh` — Badge de statusline

Lê arquivo de flag em `$CLAUDE_CONFIG_DIR/.caveman-active`. Imprime string de badge colorida pra statusline do Claude Code:
- `full` ou vazio → `[CAVEMAN]` (laranja)
- qualquer outra coisa → `[CAVEMAN:<MODE_UPPERCASED>]` (laranja)

Configurado em `settings.json` sob `statusLine.command`. Contraparte PowerShell em `hooks/caveman-statusline.ps1` para Windows.

### Instalação de hooks

**Install via plugin** — hooks conectados automaticamente pelo sistema de plugin.

**Install standalone** — `hooks/install.sh` (macOS/Linux) ou `hooks/install.ps1` (Windows) copia arquivos de hook pra `~/.claude/hooks/` e dá patch em `~/.claude/settings.json` pra registrar hooks SessionStart e UserPromptSubmit mais statusline.

**Desinstalar** — `hooks/uninstall.sh` / `hooks/uninstall.ps1` remove arquivos de hook e dá patch no settings.json.

---

## Sistema de skills

Skills = arquivos Markdown com frontmatter YAML consumidos pelo sistema de skill/plugin do Claude Code e por `npx skills` para outros agentes.

### Níveis de intensidade

Definidos em `skills/caveman/SKILL.md`. Três níveis: `lite`, `full` (padrão), `ultra`. Persiste até mudar ou sessão acabar.

### Regra de auto-clareza

Caveman cai pra prosa normal em: avisos de segurança, confirmações de ação irreversível, sequências multi-passo onde ambiguidade de fragmento arrisca má leitura, usuário confuso ou repetindo pergunta. Retoma depois. Definido na skill — preserve em qualquer edição de SKILL.md.

### caveman-compress

Sub-skill em `caveman-compress/SKILL.md`. Recebe caminho de arquivo, comprime prosa para estilo caveman, escreve no caminho original, salva backup em `<filename>.original.md`. Valida headings, blocos de código, URLs, caminhos de arquivo, comandos preservados. Retry até 2 vezes em falha com patches pontuais apenas. Requer Python 3.10+.

### caveman-commit / caveman-review

Skills independentes em `skills/caveman-commit/SKILL.md` e `skills/caveman-review/SKILL.md`. Ambas têm frontmatter próprio de `description` e `name` pra carregarem independentemente. caveman-commit: Conventional Commits, assunto ≤50 chars. caveman-review: comentários em uma linha no formato `L<linha>: <severidade> <problema>. <correção>.`.

---

## Distribuição por agente

Como caveman chega em cada tipo de agente:

| Agente | Mecanismo | Auto-ativa? |
|-------|-----------|----------------|
| Claude Code | Plugin (hooks + skills) ou hooks standalone | Sim — hook SessionStart injeta regras |
| Codex | Plugin em `plugins/caveman/` mais `.codex/hooks.json` e `.codex/config.toml` do repo | Sim no macOS/Linux — hook SessionStart |
| Gemini CLI | Extensão com arquivo de contexto `GEMINI.md` | Sim — arquivo de contexto carrega toda sessão |
| Cursor | `.cursor/rules/caveman.mdc` com `alwaysApply: true` | Sim — rule always-on |
| Windsurf | `.windsurf/rules/caveman.md` com `trigger: always_on` | Sim — rule always-on |
| Cline | `.clinerules/caveman.md` (auto-descoberto) | Sim — Cline injeta todos arquivos .clinerules |
| Copilot | `.github/copilot-instructions.md` + `AGENTS.md` | Sim — instruções de repo inteiro |
| Outros | `npx skills add JuliusBrussee/caveman` | Não — usuário precisa falar `/caveman` cada sessão |

Para agentes sem sistema de hook, snippet mínimo always-on vive no README sob "Want it always on?" — mantenha atualizado com `rules/caveman-activate.md`.

---

## Evals

`evals/` tem harness de três braços:
- `__baseline__` — sem system prompt
- `__terse__` — `Answer concisely.`
- `<skill>` — `Answer concisely.\n\n{SKILL.md}`

Delta honesto = **skill vs terse**, não skill vs baseline. Comparação com baseline confunde skill com concisão genérica — isso é trapaça. Harness projetada pra prevenir isso.

`llm_run.py` chama `claude -p --system-prompt ...` por (prompt, braço), salva em `evals/snapshots/results.json`. `measure.py` lê snapshot offline com tiktoken (BPE da OpenAI — aproxima tokenizer do Claude, razões significativas, números absolutos aproximados).

Adicionar skill: coloque `skills/<nome>/SKILL.md`. Harness auto-descobre. Adicionar prompt: anexe linha a `evals/prompts/en.txt`.

Snapshots comitados no git. CI lê sem chamadas de API. Só regenere quando SKILL.md ou prompts mudam.

---

## Benchmarks

`benchmarks/` roda prompts reais pela API Claude (não Claude Code CLI), registra contagens brutas de tokens. Resultados comitados como JSON em `benchmarks/results/`. Tabela de benchmark no README gerada a partir dos resultados — atualize ao regenerar.

Para reproduzir: `uv run python benchmarks/run.py` (precisa de `ANTHROPIC_API_KEY` em `.env.local`).

---

## Regras-chave para agentes trabalhando aqui

- Edite `skills/caveman/SKILL.md` para mudanças de comportamento. Nunca edite cópias sincronizadas.
- Edite `rules/caveman-activate.md` para mudanças de regra de auto-ativação. Nunca edite cópias de rule específicas por agente.
- README é o arquivo mais importante para impacto voltado ao usuário. Otimize para leitores não-técnicos. Preserve a voz caveman.
- Números de benchmark e eval precisam ser reais. Nunca fabrique nem estime.
- Workflow de CI commita de volta na main após merge. Considere isso ao checar estado da branch.
- Arquivos de hook precisam falhar silencioso em todos erros de filesystem. Nunca deixe crash de hook bloquear início de sessão.
- Qualquer escrita nova de arquivo de flag precisa passar por `safeWriteFlag()` em `caveman-config.js`. `fs.writeFileSync` direto em caminhos previsíveis de propriedade do usuário reabre a superfície de ataque de clobber por symlink.
- Hooks precisam respeitar env var `CLAUDE_CONFIG_DIR`, não hardcodar `~/.claude`. Mesmo para `install.sh` / `install.ps1` / scripts de statusline.
