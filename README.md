<p align="center">
  <img src="https://em-content.zobj.net/source/apple/391/rock_1faa8.png" width="120" />
</p>

<h1 align="center">cavernoso</h1>

<p align="center">
  <strong>fork pt-BR de caveman — por que usar muito token se pouco resolve</strong>
</p>

> **Nota:** Este é um fork em português brasileiro de [caveman](https://github.com/JuliusBrussee/caveman) (upstream por Julius Brussee). Toda a documentação, skills, hooks e commands foram traduzidos para pt-BR, preservando o comportamento original. Para a versão em inglês, veja o [repositório upstream](https://github.com/JuliusBrussee/caveman).

<p align="center">
  <a href="https://github.com/alfredogazperi/cavernoso/stargazers"><img src="https://img.shields.io/github/stars/alfredogazperi/cavernoso?style=flat&color=yellow" alt="Stars"></a>
  <a href="https://github.com/alfredogazperi/cavernoso/commits/pt-br"><img src="https://img.shields.io/github/last-commit/alfredogazperi/cavernoso?style=flat" alt="Last Commit"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/alfredogazperi/cavernoso?style=flat" alt="License"></a>
</p>

<p align="center">
  <a href="#antes--depois">Antes/Depois</a> •
  <a href="#instalação">Instalação</a> •
  <a href="#níveis-de-intensidade">Níveis</a> •
  <a href="#skills-do-caveman">Skills</a> •
  <a href="#benchmarks">Benchmarks</a> •
  <a href="#evals">Evals</a>
</p>

<p align="center">
  <strong>🪨 Ecossistema Caveman</strong> &nbsp;·&nbsp;
  <strong>caveman</strong> <em>falar menos</em> <sub>(você está aqui)</sub> &nbsp;·&nbsp;
  <a href="https://github.com/JuliusBrussee/cavemem">cavemem</a> <em>lembrar mais</em> &nbsp;·&nbsp;
  <a href="https://github.com/JuliusBrussee/cavekit">cavekit</a> <em>construir melhor</em>
</p>

---

Uma skill/plugin do [Claude Code](https://docs.anthropic.com/en/docs/claude-code) e plugin do Codex que faz o agente falar como caveman — cortando **~75% dos tokens de saída** mantendo precisão técnica completa. Agora com [modo 文言文](#modo-文言文-wenyan), [commits terse](#caveman-commit), [code reviews em uma linha](#caveman-review) e uma [ferramenta de compressão](#caveman-compress) que corta **~46% dos tokens de entrada** toda sessão.

Baseado na observação viral de que falar como caveman reduz drasticamente o uso de tokens pelo LLM sem perder substância técnica. Então transformamos isso em um install de uma linha.

## Antes / Depois

<table>
<tr>
<td width="50%">

### 🗣️ Claude Normal (69 tokens)

> "A razão pela qual seu componente React está re-renderizando é provavelmente porque você está criando uma nova referência de objeto em cada ciclo de render. Quando você passa um objeto inline como prop, a comparação rasa do React vê como objeto diferente toda vez, o que dispara um re-render. Eu recomendaria usar useMemo para memoizar o objeto."

</td>
<td width="50%">

### 🪨 Claude Caveman (19 tokens)

> "Ref nova de objeto cada render. Prop objeto inline = ref nova = re-render. Envolve em `useMemo`."

</td>
</tr>
<tr>
<td>

### 🗣️ Claude Normal

> "Claro! Ficarei feliz em te ajudar. O problema que você está enfrentando provavelmente é causado pelo seu middleware de autenticação não validando corretamente a expiração do token. Deixa eu dar uma olhada e sugerir uma correção."

</td>
<td>

### 🪨 Claude Caveman

> "Bug no middleware auth. Check de expiração de token usa `<` não `<=`. Fix:"

</td>
</tr>
</table>

**Mesmo fix. 75% menos palavra. Cérebro ainda grande.**

**Escolha seu nível de grunhido:**

<table>
<tr>
<td width="25%">

#### 🪶 Lite

> "Seu componente re-renderiza porque cria uma nova referência de objeto a cada render. Props de objeto inline falham a comparação rasa toda vez. Envolve em `useMemo`."

</td>
<td width="25%">

#### 🪨 Full

> "Ref nova de objeto cada render. Prop objeto inline = ref nova = re-render. Envolve em `useMemo`."

</td>
<td width="25%">

#### 🔥 Ultra

> "Prop obj inline → ref nova → re-render. `useMemo`."

</td>
<td width="25%">

#### 📜 文言文

> "物出新參照，致重繪。useMemo Wrap之。"

</td>
</tr>
</table>

**Mesma resposta. Você escolhe quantas palavras.**

```
┌─────────────────────────────────────┐
│  TOKENS ECONOMIZADOS   ████████ 75% │
│  PRECISÃO TÉCNICA      ████████ 100%│
│  AUMENTO DE VELOCIDADE ████████ ~3x │
│  VIBE                  ████████ OOG │
└─────────────────────────────────────┘
```

- **Resposta mais rápida** — menos token pra gerar = velocidade vai brrr
- **Mais fácil de ler** — sem parede de texto, só a resposta
- **Mesma precisão** — toda info técnica preservada, só penugem removida ([ciência diz](https://arxiv.org/abs/2604.00025))
- **Economiza grana** — ~71% menos token de saída = menos custo
- **Divertido** — todo code review vira comédia

## Instalação

Escolha seu agente. Um comando. Pronto.

| Agente | Install |
|-------|---------|
| **Claude Code** | `claude plugin marketplace add alfredogazperi/cavernoso && claude plugin install caveman@caveman` |
| **Codex** | Clone do repo → `/plugins` → Busque "Caveman" → Install |
| **Gemini CLI** | `gemini extensions install https://github.com/alfredogazperi/cavernoso` |
| **Cursor** | `npx skills add alfredogazperi/cavernoso -a cursor` |
| **Windsurf** | `npx skills add alfredogazperi/cavernoso -a windsurf` |
| **Copilot** | `npx skills add alfredogazperi/cavernoso -a github-copilot` |
| **Cline** | `npx skills add alfredogazperi/cavernoso -a cline` |
| **Qualquer outro** | `npx skills add alfredogazperi/cavernoso` |

Instala uma vez. Usa toda sessão nesse alvo depois disso. Uma pedra. Só isso.

### O que você leva

Auto-ativação vem embutida para Claude Code, Gemini CLI, e o setup do Codex local do repo abaixo. `npx skills add` instala a skill para outros agentes, mas **não** instala arquivos de rule/instrução do repo, então Caveman não auto-inicia lá a menos que você adicione o snippet always-on abaixo.

| Funcionalidade | Claude Code | Codex | Gemini CLI | Cursor | Windsurf | Cline | Copilot |
|---------|:-----------:|:-----:|:----------:|:------:|:--------:|:-----:|:-------:|
| Modo caveman | Y | Y | Y | Y | Y | Y | Y |
| Auto-ativa toda sessão | Y | Y¹ | Y | —² | —² | —² | —² |
| Comando `/caveman` | Y | Y¹ | Y | — | — | — | — |
| Troca de modo (lite/full/ultra) | Y | Y¹ | Y | Y³ | Y³ | — | — |
| Badge de statusline | Y⁴ | — | — | — | — | — | — |
| caveman-commit | Y | — | Y | Y | Y | Y | Y |
| caveman-review | Y | — | Y | Y | Y | Y | Y |
| caveman-compress | Y | Y | Y | Y | Y | Y | Y |
| caveman-help | Y | — | Y | Y | Y | Y | Y |

> [!NOTE]
> Auto-ativação funciona diferente por agente: Claude Code usa hooks SessionStart, o setup dogfood do Codex neste repo usa `.codex/hooks.json`, Gemini usa arquivos de contexto. Cursor/Windsurf/Cline/Copilot podem ficar always-on, mas `npx skills add` instala só a skill, não os arquivos de rule/instrução do repo.
>
> ¹ Codex usa sintaxe `$caveman`, não `/caveman`. Este repo distribui `.codex/hooks.json`, então caveman auto-inicia quando você roda Codex dentro deste repo. O plugin instalado em si te dá `$caveman`; copie o mesmo hook para outro repo se quiser comportamento always-on lá também. caveman-commit e caveman-review não estão no bundle do plugin do Codex — use os arquivos SKILL.md diretamente.
> ² Adicione o snippet "Quer sempre ligado?" abaixo ao system prompt ou arquivo de rule desses agentes se quiser ativação no início da sessão.
> ³ Cursor e Windsurf recebem o SKILL.md completo com todos os níveis de intensidade. Troca de modo funciona sob demanda via skill; sem slash command.
> ⁴ Disponível no Claude Code, mas install via plugin só sugere setup. Standalone `install.sh` / `install.ps1` configura automaticamente quando não existe `statusLine` customizado.

<details>
<summary><strong>Claude Code — detalhes completos</strong></summary>

O install do plugin te dá skills + hooks de auto-carregamento. Se nenhum `statusLine` customizado está configurado, Caveman sugere que Claude ofereça setup do badge na primeira sessão.

```bash
claude plugin marketplace add alfredogazperi/cavernoso
claude plugin install caveman@caveman
```

**Hooks standalone (sem plugin):** Se preferir não usar o sistema de plugin:
```bash
# macOS / Linux / WSL
bash <(curl -s https://raw.githubusercontent.com/alfredogazperi/cavernoso/pt-br/hooks/install.sh)

# Windows (PowerShell)
irm https://raw.githubusercontent.com/alfredogazperi/cavernoso/pt-br/hooks/install.ps1 | iex
```

Ou a partir de um clone local: `bash hooks/install.sh` / `powershell -File hooks\install.ps1`

Desinstalar: `bash hooks/uninstall.sh` ou `powershell -File hooks\uninstall.ps1`

**Badge de statusline:** Mostra `[CAVEMAN]`, `[CAVEMAN:ULTRA]`, etc. na sua barra de status do Claude Code.

- **Install via plugin:** Se você ainda não tem `statusLine` customizado, Claude deve oferecer configurar na primeira sessão
- **Install standalone:** Configurado automaticamente por `install.sh` / `install.ps1` a menos que você já tenha um statusline customizado
- **Statusline customizado:** Instalador deixa seu statusline existente em paz. Veja [`hooks/README.md`](hooks/README.md) para o snippet de merge

</details>

<details>
<summary><strong>Codex — detalhes completos</strong></summary>

**macOS / Linux:**
1. Clone do repo → Abra Codex no diretório do repo → `/plugins` → Busque "Caveman" → Install
2. Auto-start local do repo já está conectado por `.codex/hooks.json` + `.codex/config.toml`

**Windows:**
1. Habilite symlinks primeiro: `git config --global core.symlinks true` (requer Developer Mode ou admin)
2. Clone do repo → Abra VS Code → Configurações do Codex → Plugins → encontre "Caveman" sob marketplace local → Install → Reload Window
3. Hooks do Codex estão atualmente desabilitados no Windows, então use `$caveman` pra iniciar manualmente

Este repo também distribui `.codex/hooks.json` e habilita hooks em `.codex/config.toml`, então caveman auto-ativa enquanto você roda Codex dentro deste repo no macOS/Linux. O plugin instalado te dá `$caveman`; se quiser comportamento always-on em outros repos também, copie o mesmo hook `SessionStart` pra lá e habilite:

```toml
[features]
codex_hooks = true
```

</details>

<details>
<summary><strong>Gemini CLI — detalhes completos</strong></summary>

```bash
gemini extensions install https://github.com/alfredogazperi/cavernoso
```

Update: `gemini extensions update caveman` · Desinstalar: `gemini extensions uninstall caveman`

Auto-ativa via arquivo de contexto `GEMINI.md`. Também distribui comandos Gemini customizados:
- `/caveman` — troca nível de intensidade (lite/full/ultra/wenyan)
- `/caveman-commit` — gera mensagem de commit terse
- `/caveman-review` — code review em uma linha

</details>

<details>
<summary><strong>Cursor / Windsurf / Cline / Copilot — detalhes completos</strong></summary>

`npx skills add` instala só o arquivo de skill — **não** instala o arquivo de rule/instrução do agente, então caveman não auto-inicia. Para always-on, adicione o snippet "Quer sempre ligado?" abaixo às rules ou system prompt do seu agente.

| Agente | Comando | Não instalado | Troca de modo | Local always-on |
|-------|---------|--------------|:--------------:|--------------------|
| Cursor | `npx skills add alfredogazperi/cavernoso -a cursor` | `.cursor/rules/caveman.mdc` | Y | Rules do Cursor |
| Windsurf | `npx skills add alfredogazperi/cavernoso -a windsurf` | `.windsurf/rules/caveman.md` | Y | Rules do Windsurf |
| Cline | `npx skills add alfredogazperi/cavernoso -a cline` | `.clinerules/caveman.md` | — | Rules do Cline ou system prompt |
| Copilot | `npx skills add alfredogazperi/cavernoso -a github-copilot` | `.github/copilot-instructions.md` + `AGENTS.md` | — | Instruções customizadas do Copilot |

Desinstalar: `npx skills remove caveman`

Copilot funciona com Chat, Edits e Coding Agent.

</details>

<details>
<summary><strong>Qualquer outro agente (opencode, Roo, Amp, Goose, Kiro, e mais 40+)</strong></summary>

[npx skills](https://github.com/vercel-labs/skills) suporta mais de 40 agentes:

```bash
npx skills add alfredogazperi/cavernoso           # auto-detecta agente
npx skills add alfredogazperi/cavernoso -a amp
npx skills add alfredogazperi/cavernoso -a augment
npx skills add alfredogazperi/cavernoso -a goose
npx skills add alfredogazperi/cavernoso -a kiro-cli
npx skills add alfredogazperi/cavernoso -a roo
# ... e muitos outros
```

Desinstalar: `npx skills remove caveman`

> **Nota Windows:** `npx skills` usa symlinks por padrão. Se symlinks falharem, adicione `--copy`: `npx skills add alfredogazperi/cavernoso --copy`

**Importante:** Esses agentes não têm sistema de hook, então caveman não vai auto-iniciar. Fale `/caveman` ou "talk like caveman" para ativar a cada sessão.

**Quer sempre ligado?** Cole isto no system prompt ou arquivo de rules do seu agente — caveman fica ativo desde a primeira mensagem, toda sessão:

```
Terse like caveman. Technical substance exact. Only fluff die.
Drop: articles, filler (just/really/basically), pleasantries, hedging.
Fragments OK. Short synonyms. Code unchanged.
Pattern: [thing] [action] [reason]. [next step].
ACTIVE EVERY RESPONSE. No revert after many turns. No filler drift.
Code/commits/PRs: normal. Off: "stop caveman" / "normal mode".
```

Onde colocar:
| Agente | Arquivo |
|-------|------|
| opencode | `.config/opencode/AGENTS.md` |
| Roo | `.roo/rules/caveman.md` |
| Amp | system prompt do seu workspace |
| Outros | system prompt ou arquivo de rules do seu agente |

</details>

## Uso

Dispare com:
- `/caveman` ou Codex `$caveman`
- "talk like caveman"
- "caveman mode"
- "less tokens please"

Pare com: "stop caveman" ou "normal mode"

### Níveis de intensidade

| Nível | Trigger | O que faz |
|-------|---------|------------|
| **Lite** | `/caveman lite` | Drop filler, mantém gramática. Profissional mas sem penugem |
| **Full** | `/caveman full` | Caveman padrão. Drop artigos, fragmentos, grunhido completo |
| **Ultra** | `/caveman ultra` | Compressão máxima. Telegráfico. Abrevia tudo |

### Modo 文言文 (Wenyan)

Compressão literária chinesa clássica — mesma precisão técnica, mas na linguagem escrita mais eficiente em tokens que os humanos já inventaram.

| Nível | Trigger | O que faz |
|-------|---------|------------|
| **Wenyan-Lite** | `/caveman wenyan-lite` | Semi-clássico. Gramática intacta, filler fora |
| **Wenyan-Full** | `/caveman wenyan` | 文言文 completo. Concisão clássica máxima |
| **Wenyan-Ultra** | `/caveman wenyan-ultra` | Extremo. Sábio antigo no orçamento |

Nível fica até você mudar ou sessão acabar.

## Skills do Caveman

### caveman-commit

`/caveman-commit` — mensagens de commit terse. Conventional Commits. Assunto ≤50 chars. Por quê em vez do quê.

### caveman-review

`/caveman-review` — comentários de PR em uma linha: `L42: 🔴 bug: user null. Add guard.` Sem pigarrear.

### caveman-help

`/caveman-help` — cartão de referência rápida. Todos os modos, skills, comandos, a um comando de distância.

### caveman-compress

`/caveman:compress <caminho-do-arquivo>` — caveman faz Claude *falar* com menos tokens. **Compress** faz Claude *ler* menos tokens.

Seu `CLAUDE.md` carrega no **início de toda sessão**. Caveman Compress reescreve arquivos de memória em estilo caveman para que Claude leia menos — sem você perder o original legível por humanos.

```
/caveman:compress CLAUDE.md
```

```
CLAUDE.md          ← comprimido (Claude lê este toda sessão — menos tokens)
CLAUDE.original.md ← backup legível por humanos (você lê e edita este)
```

| Arquivo | Original | Comprimido | Economia |
|------|----------:|----------:|------:|
| `claude-md-preferences.md` | 706 | 285 | **59.6%** |
| `project-notes.md` | 1145 | 535 | **53.3%** |
| `claude-md-project.md` | 1122 | 636 | **43.3%** |
| `todo-list.md` | 627 | 388 | **38.1%** |
| `mixed-with-code.md` | 888 | 560 | **36.9%** |
| **Média** | **898** | **481** | **46%** |

Blocos de código, URLs, caminhos de arquivo, comandos, headings, datas, números de versão — qualquer coisa técnica passa sem toque. Só a prosa é comprimida. Veja o [README completo do caveman-compress](caveman-compress/README.md) para detalhes. [Nota de segurança](./caveman-compress/SECURITY.md): Snyk flagueia isto como High Risk por causa de padrões de subprocess/arquivo — é falso positivo.

## Benchmarks

Contagens reais de tokens da API Claude ([reproduza você mesmo](benchmarks/)):

<!-- BENCHMARK-TABLE-START -->
| Tarefa | Normal (tokens) | Caveman (tokens) | Economia |
|------|---------------:|----------------:|------:|
| Explain React re-render bug | 1180 | 159 | 87% |
| Fix auth middleware token expiry | 704 | 121 | 83% |
| Set up PostgreSQL connection pool | 2347 | 380 | 84% |
| Explain git rebase vs merge | 702 | 292 | 58% |
| Refactor callback to async/await | 387 | 301 | 22% |
| Architecture: microservices vs monolith | 446 | 310 | 30% |
| Review PR for security issues | 678 | 398 | 41% |
| Docker multi-stage build | 1042 | 290 | 72% |
| Debug PostgreSQL race condition | 1200 | 232 | 81% |
| Implement React error boundary | 3454 | 456 | 87% |
| **Média** | **1214** | **294** | **65%** |

*Faixa: 22%–87% de economia pelos prompts.*
<!-- BENCHMARK-TABLE-END -->

> [!IMPORTANT]
> Caveman só afeta tokens de saída — tokens de thinking/reasoning ficam intactos. Caveman não deixa cérebro menor. Caveman deixa *boca* menor. Maior ganho é **legibilidade e velocidade**, economia de custo é bônus.

Um paper de março de 2026 ["Brevity Constraints Reverse Performance Hierarchies in Language Models"](https://arxiv.org/abs/2604.00025) descobriu que restringir modelos grandes a respostas breves **melhorou a precisão em 26 pontos percentuais** em certos benchmarks e reverteu completamente hierarquias de performance. Verboso nem sempre é melhor. Às vezes menos palavra = mais certo.

## Evals

Caveman não só afirma 75%. Caveman **prova**.

O diretório `evals/` tem uma harness de eval de três braços que mede compressão real de tokens contra um controle próprio — não só "verboso vs skill" mas "terse vs skill". Porque comparar caveman a Claude verboso confunde a skill com concisão genérica. Isso é trapaça. Caveman não trapaceia.

```bash
# Roda o eval (precisa do CLI claude)
uv run python evals/llm_run.py

# Lê resultados (sem API key, roda offline)
uv run --with tiktoken python evals/measure.py
```

## Dê star neste repo

Se caveman te economizar muito token, muita grana — deixe muita estrela. ⭐

[![Star History Chart](https://api.star-history.com/svg?repos=alfredogazperi/cavernoso&type=Date)](https://star-history.com/#alfredogazperi/cavernoso&Date)

## 🪨 O Ecossistema Caveman

Três ferramentas. Uma filosofia: **agente faz mais com menos**.

| Repo | O que | One-liner |
|------|------|-----------|
| [**caveman**](https://github.com/JuliusBrussee/caveman) *(upstream)* | Skill de compressão de saída | *por que usar muito token se pouco resolve* — ~75% menos tokens de saída através de Claude Code, Cursor, Gemini, Codex |
| [**cavemem**](https://github.com/JuliusBrussee/cavemem) | Memória persistente cross-agent | *por que agente esquece se agente pode lembrar* — SQLite comprimido + MCP, local por padrão |
| [**cavekit**](https://github.com/JuliusBrussee/cavekit) | Loop autônomo de build spec-driven | *por que agente adivinha se agente pode saber* — linguagem natural → kits → build paralelo → verificado |

Eles compõem: **cavekit** orquestra o build, **caveman** comprime o que o agente *fala*, **cavemem** comprime o que o agente *lembra*. Instale um, alguns ou todos — cada um é independente.

## Também por Julius Brussee

- **[Revu](https://github.com/JuliusBrussee/revu-swift)** — app de estudo macOS local-first com repetição espaçada FSRS, decks, provas e guias de estudo. [revu.cards](https://revu.cards)

## Licença

MIT — livre como muito mamute em planície aberta.
