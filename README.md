<p align="center">
  <img src="https://em-content.zobj.net/source/apple/391/rock_1faa8.png" width="120" />
</p>

<h1 align="center">cavernoso</h1>

<p align="center">
  <strong>fork pt-BR de caveman — por que gastar muito token se pouco resolve</strong>
</p>

<p align="center">
  <a href="https://github.com/alfredogazperi/cavernoso/stargazers"><img src="https://img.shields.io/github/stars/alfredogazperi/cavernoso?style=flat&color=yellow" alt="Stars"></a>
  <a href="https://github.com/alfredogazperi/cavernoso/commits/pt-br"><img src="https://img.shields.io/github/last-commit/alfredogazperi/cavernoso?style=flat" alt="Last Commit"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/alfredogazperi/cavernoso?style=flat" alt="License"></a>
</p>

<p align="center">
  <a href="#o-que-é">O que é</a> •
  <a href="#instalação">Instalação</a> •
  <a href="#antes--depois">Antes/Depois</a> •
  <a href="#níveis">Níveis</a> •
  <a href="#skills">Skills</a> •
  <a href="#sobre">Sobre</a>
</p>

---

## O que é

Plugin do [Claude Code](https://docs.anthropic.com/en/docs/claude-code) que faz o Claude responder em **pt-BR cavernoso** — frases curtas, sem filler, sem pleonasmo, sem "é importante ressaltar que". Corta cerca de **75% dos tokens de saída** mantendo toda a precisão técnica.

Inclui também:

- **[`caveman-compress`](#caveman-compress)** — comprime seus `CLAUDE.md` e notas pra o Claude ler menos token toda sessão (~46% a menos na leitura).
- **[`caveman-commit`](#caveman-commit)** — mensagens de commit Conventional Commits, curtas, foco no *por quê*.
- **[`caveman-review`](#caveman-review)** — code review em uma linha por achado, com severidade.
- **[`caveman-help`](#caveman-help)** — cartão de referência dos modos e comandos.

Fork pt-BR de [caveman](https://github.com/JuliusBrussee/caveman) por Julius Brussee. Traduzido e adaptado pra português brasileiro — com pré-processamento determinístico que remove pleonasmos (*subir pra cima*, *entrar pra dentro*), expressões vazias (*vale a pena mencionar que*) e filler antes mesmo de chamar o LLM.

## Instalação

**Só para Claude Code.** Não suporta outros agentes — se quiser multi-agente, veja o [upstream em inglês](https://github.com/JuliusBrussee/caveman).

Via marketplace [gazperi-lab](https://github.com/alfredogazperi/gazperi-lab):

```bash
claude plugin marketplace add alfredogazperi/gazperi-lab
claude plugin install cavernoso@gazperi-lab
```

Reinicia o Claude Code. Pronto. Hooks carregam sozinhos, statusline mostra `[CAVERNOSO]` quando modo ativo.

> [!NOTE]
> Se der erro de clone via SSH, roda `git config --global url."https://github.com/".insteadOf "git@github.com:"` antes.

### Ativar/desativar por sessão

- Ativa: `/caveman`, "fala como cavernoso", "ativa cavernoso", "modo cavernoso"
- Desativa: "para", "desliga cavernoso", "modo normal"

## Antes / Depois

<table>
<tr>
<td width="50%">

### 🗣️ Claude normal (72 tokens)

> "É importante notar que o seu componente React está re-renderizando provavelmente porque você está criando uma nova referência de objeto a cada ciclo de render. Quando você passa um objeto inline como prop, a comparação rasa do React vê como objeto diferente toda vez, o que acaba disparando um re-render. Eu recomendaria envolver em `useMemo` para memoizar."

</td>
<td width="50%">

### 🪨 Claude cavernoso (17 tokens)

> "Prop objeto inline = ref nova cada render = re-render. Envolve em `useMemo`."

</td>
</tr>
<tr>
<td>

### 🗣️ Claude normal

> "Com certeza, fico feliz em ajudar! O problema que você está enfrentando provavelmente é causado pelo middleware de autenticação não validando corretamente a expiração do token. Deixa eu dar uma olhada e sugerir uma correção apropriada."

</td>
<td>

### 🪨 Claude cavernoso

> "Bug no middleware auth. Check de expiração usa `<` em vez de `<=`. Fix:"

</td>
</tr>
<tr>
<td>

### 🗣️ Claude normal

> "Basicamente, o problema aqui é que o seu endpoint está fazendo N+1 queries. Cada vez que você itera sobre os pedidos, está indo ao banco buscar o cliente separadamente. Seria interessante considerar usar um JOIN ou prefetch para resolver isso de forma mais eficiente."

</td>
<td>

### 🪨 Claude cavernoso

> "N+1 no endpoint. Loop pega cliente por pedido. Use JOIN ou prefetch."

</td>
</tr>
</table>

**Mesmo fix. 75% menos palavra. Cérebro continua grande.**

## Níveis

| Nível | Trigger | Exemplo |
|---|---|---|
| **Lite** | `/caveman lite` | "Seu componente re-renderiza porque cria nova referência de objeto. Envolve em `useMemo`." |
| **Full** | `/caveman full` | "Prop objeto inline = ref nova = re-render. Envolve em `useMemo`." |
| **Ultra** | `/caveman ultra` | "Prop obj inline → ref nova → re-render. `useMemo`." |

Nível persiste até trocar ou terminar a sessão.

## Skills

### caveman-compress

`/caveman:compress <arquivo>` — reescreve seu `CLAUDE.md` em estilo cavernoso pro Claude ler menos token toda sessão, sem você perder o original legível.

```
/caveman:compress CLAUDE.md
```

```
CLAUDE.md          ← comprimido (Claude lê toda sessão)
CLAUDE.original.md ← backup legível (você edita este)
```

**Pipeline em dois passos:**

1. **Pré-processamento determinístico pt-BR** (Python, sem LLM) — remove pleonasmos (`subir para cima` → `subir`), redundâncias (`pelo fato de que` → `porque`), expressões vazias (`é importante notar que` → nada), filler isolado (`basicamente,` → nada). Cerca de 20% de redução antes do modelo sequer ler o arquivo.
2. **Compressão via Claude** — o que sobrou de prosa passa pelo modelo com prompt cavernoso.

Blocos de código, URLs, caminhos, comandos, headers, tabelas e frontmatter passam intactos. Só prosa é tocada.

Ver [`caveman-compress/README.md`](caveman-compress/README.md) e [nota de segurança](./caveman-compress/SECURITY.md).

### caveman-commit

`/caveman-commit` — gera mensagem em [Conventional Commits](https://www.conventionalcommits.org/), assunto ≤50 chars, explica o *por quê*.

Exemplo de saída real:

```
fix(auth): middleware usava < em vez de <= na expiração

Token exato no segundo de expirar era aceito como válido,
causando requests 401 intermitentes logo após refresh.
```

### caveman-review

`/caveman-review` — code review em uma linha por achado. Formato: `L<linha>: <severidade> <problema>. <fix>.`

```
L42: bug: user pode ser null aqui. Adicionar guard.
L78: risk: sem retry, falha silenciosa em rede.
L104: nit: nome melhor: `taxaConversao` em vez de `tc`.
L130: q: por que 30s de timeout e não 5?
```

Severidades: `bug`, `risk`, `nit`, `q`. Sem elogio, sem "ótimo trabalho!".

### caveman-help

`/caveman-help` — cartão de referência com todos os modos, comandos, gatilhos e skills. Abre quando não lembrar.

## Pré-processamento pt-BR

O `preprocess.py` trata de forma determinística (sem LLM) as seguintes classes de redução:

| Classe | Exemplo | Ação |
|---|---|---|
| Redundância | *pelo fato de que* | → *porque* |
| Redundância | *com o objetivo de* | → *para* |
| Redundância | *em virtude de* | → *por* |
| Pleonasmo | *subir para cima* | → *subir* |
| Pleonasmo | *entrar para dentro* | → *entrar* |
| Pleonasmo | *há tempos atrás* | → *há tempos* |
| Expressão vazia | *é importante notar que* | → remove |
| Expressão vazia | *vale a pena mencionar que* | → remove |
| Filler isolado | *basicamente,* | → remove |
| Filler isolado | *na verdade,* | → remove |

Regiões protegidas: blocos de código, código inline, URLs, links markdown, caminhos, frontmatter YAML, tabelas pipe. Nada técnico é tocado.

## Sobre

Mantido por **[Alfredo Gazperi](https://github.com/alfredogazperi)** como parte do **[Claude Lab](https://github.com/alfredogazperi/gazperi-lab)** — o braço de P&D da Gazperi dedicado a construir ferramentas em torno do Claude.

O cavernoso nasceu do uso diário: se eu passo o dia inteiro no Claude Code, cada token economizado na saída compõe. Em português, o ganho é maior ainda porque a língua acumula pleonasmos e expressões protocolares que inflam respostas sem adicionar substância. O fork calibra o upstream pra essa realidade.

A v0.1.0 é versão mínima publicável. Refinamento vem pelo uso real, não por especificação antecipada — correções no pt-BR compõem em `learnings/` da skill e viram ajustes de prompt nas versões seguintes.

**Outros plugins do Claude Lab:** veja o [marketplace gazperi-lab](https://github.com/alfredogazperi/gazperi-lab).

## Créditos

Fork de [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) (Julius Brussee). Toda a arquitetura original — hooks, skills, statusline — é do upstream. Este fork traduz, adapta ao pt-BR, remove o modo Wenyan (sem uso no meu contexto) e adiciona o pré-processamento determinístico.

## Licença

MIT — livre como mamute em planície aberta.
