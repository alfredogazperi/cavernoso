<p align="center">
  <img src="https://em-content.zobj.net/source/apple/391/rock_1faa8.png" width="80" />
</p>

<h1 align="center">caveman-compress</h1>

<p align="center">
  <strong>encolhe arquivo de memória. economiza token toda sessão.</strong>
</p>

---

Uma skill do Claude Code que comprime seus arquivos de memória de projeto (`CLAUDE.md`, todos, preferências) em formato caveman — assim toda sessão carrega menos tokens automaticamente.

Claude lê `CLAUDE.md` no início de toda sessão. Se arquivo grande, custo grande. Caveman deixa arquivo pequeno. Custo cai pra sempre.

## O que faz

```
/caveman:compress CLAUDE.md
```

```
CLAUDE.md          ← comprimido (Claude lê isto — menos tokens toda sessão)
CLAUDE.original.md ← backup legível por humanos (você edita este)
```

Original nunca perdido. Você pode ler e editar `.original.md`. Rode a skill de novo pra re-comprimir depois de editar.

## Benchmarks

Resultados reais em arquivos de projeto reais:

| Arquivo | Original | Comprimido | Economia |
|------|----------:|----------:|------:|
| `claude-md-preferences.md` | 706 | 285 | **59.6%** |
| `project-notes.md` | 1145 | 535 | **53.3%** |
| `claude-md-project.md` | 1122 | 636 | **43.3%** |
| `todo-list.md` | 627 | 388 | **38.1%** |
| `mixed-with-code.md` | 888 | 560 | **36.9%** |
| **Média** | **898** | **481** | **46%** |

Todas as validações passaram ✅ — headings, blocos de código, URLs, caminhos de arquivo preservados exatamente.

## Antes / Depois

<table>
<tr>
<td width="50%">

### 📄 Original (706 tokens)

> "Eu prefiro fortemente TypeScript com modo estrito ativado para todo código novo. Por favor não use o tipo `any` a menos que genuinamente não haja outra saída, e se usar, deixe um comentário explicando o raciocínio. Acho que gastar tempo tipando as coisas direito pega muitos bugs antes que cheguem a runtime."

</td>
<td width="50%">

### 🪨 Caveman (285 tokens)

> "Prefira TypeScript strict sempre. Sem `any` a menos inevitável — comente por quê se usar. Tipos certos pegam bug cedo."

</td>
</tr>
</table>

**Mesmas instruções. 60% menos tokens. Toda. Sessão.**

## Segurança

`caveman-compress` é flagueado como Snyk High Risk por causa de padrões de subprocess e I/O de arquivo detectados por análise estática. Isso é falso positivo — veja [SECURITY.md](./SECURITY.md) para explicação completa do que a skill faz e do que não faz.

## Instalação

Compress vem embutido com o plugin `caveman`. Instale `caveman` uma vez, depois use `/caveman:compress`.

Se precisa dos arquivos locais, a skill de compress vive em:

```bash
caveman-compress/
```

**Requer:** Python 3.10+

## Uso

```
/caveman:compress <caminho-do-arquivo>
```

Exemplos:
```
/caveman:compress CLAUDE.md
/caveman:compress docs/preferences.md
/caveman:compress todos.md
```

### Quais arquivos funcionam

| Tipo | Comprime? |
|------|-----------|
| `.md`, `.txt`, `.rst` | ✅ Sim |
| Sem extensão em linguagem natural | ✅ Sim |
| `.py`, `.js`, `.ts`, `.json`, `.yaml` | ❌ Pula (código/config) |
| `*.original.md` | ❌ Pula (arquivos de backup) |

## Como funciona

```
/caveman:compress CLAUDE.md
        ↓
detecta tipo do arquivo      (sem tokens)
        ↓
Claude comprime              (tokens — uma chamada)
        ↓
valida saída                 (sem tokens)
  checa: headings, blocos de código, URLs, caminhos, bullets
        ↓
se erros: Claude corrige só problemas pontuais   (tokens — correção pontual)
  NÃO recomprime — só remenda partes quebradas
        ↓
retry até 2 vezes
        ↓
escreve comprimido → CLAUDE.md
escreve original   → CLAUDE.original.md
```

Só duas coisas usam tokens: compressão inicial + correção pontual se validação falhar. Todo o resto é Python local.

## O que é preservado

Caveman comprime linguagem natural. Nunca toca em:

- Blocos de código (` ``` ` cercados ou indentados)
- Código inline (`` `conteúdo entre crases` ``)
- URLs e links
- Caminhos de arquivo (`/src/components/...`)
- Comandos (`npm install`, `git commit`)
- Termos técnicos, nomes de biblioteca, nomes de API
- Headings (texto exato preservado)
- Tabelas (estrutura preservada, texto das células comprimido)
- Datas, números de versão, valores numéricos

## Por que isso importa

`CLAUDE.md` carrega no **início de toda sessão**. Um arquivo de memória de projeto de 1000 tokens custa tokens toda vez que você abre o projeto. Em 100 sessões isso é 100.000 tokens de overhead — só pra contexto que você já escreveu.

Caveman corta isso em ~46% em média. Mesmas instruções. Mesma precisão. Menos desperdício.

```
┌────────────────────────────────────────────┐
│  ECONOMIA DE TOKEN POR ARQUIVO  █████  46% │
│  SESSÕES QUE BENEFICIAM    ██████████ 100% │
│  INFORMAÇÃO PRESERVADA     ██████████ 100% │
│  TEMPO DE SETUP            █            1x │
└────────────────────────────────────────────┘
```

## Parte de Caveman

Esta skill é parte do toolkit [caveman](https://github.com/JuliusBrussee/caveman) — fazendo Claude usar menos tokens sem perder precisão.

- **caveman** — faz Claude *falar* como caveman (corta ~65% dos tokens de resposta)
- **caveman-compress** — faz Claude *ler* menos (corta ~46% dos tokens de contexto)
