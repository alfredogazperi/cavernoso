# Evals

Mede compressão real de tokens das skills caveman rodando os mesmos
prompts pelo Claude Code sob três condições e comparando as contagens
de tokens de saída geradas.

## Os três braços

| Braço | System prompt |
|-----|--------------|
| `__baseline__` | nenhum |
| `__terse__` | `Answer concisely.` |
| `<skill>` | `Answer concisely.\n\n{SKILL.md}` |

O delta honesto de qualquer skill é **`<skill>` vs `__terse__`** — ou seja,
quanto a skill em si adiciona em cima de uma instrução simples "seja terse".
Comparar uma skill ao baseline sem system prompt confunde a skill
com o pedido genérico de concisão, que foi o que uma versão anterior
desta harness fazia e é por isso que os números dela eram inflados.

## Por que este design

- **Saída real de LLM**, não exemplos escritos à mão (sem circularidade).
- **Mesmo Claude Code** que as skills miram — sem API key separada.
- **Snapshot comitado no git** pra rodadas de CI serem determinísticas e
  gratuitas, e pra qualquer mudança nos números ser revisável como diff.
- **Braço de controle** isola a contribuição da skill do efeito genérico
  de "ser terse".

## Arquivos

- `prompts/en.txt` — lista fixa de perguntas de dev, uma por linha.
- `llm_run.py` — roda `claude -p --system-prompt …` por (prompt, braço),
  captura saída real de LLM, escreve `snapshots/results.json` junto com
  metadata (modelo, versão do CLI, timestamp de geração).
- `measure.py` — lê o snapshot, conta tokens com tiktoken
  `o200k_base`, imprime tabela markdown com mediana / média / min / max /
  stdev através dos prompts.
- `snapshots/results.json` — fonte da verdade comitada, regenerada só
  quando arquivos SKILL.md ou prompts mudam.

## Atualizar o snapshot (requer CLI `claude` logado)

```bash
uv run python evals/llm_run.py
```

Isso chama Claude uma vez por prompt × (N skills + 2 braços de controle). Use
um modelo pequeno pra manter barato:

```bash
CAVEMAN_EVAL_MODEL=claude-haiku-4-5 uv run python evals/llm_run.py
```

## Ler o snapshot (sem LLM, sem API key, roda em CI)

```bash
uv run --with tiktoken python evals/measure.py
```

## Adicionando um prompt

Anexe uma linha a `prompts/en.txt`, depois atualize o snapshot.

## Adicionando uma skill

Coloque um `skills/<nome>/SKILL.md`, depois atualize o snapshot. `llm_run.py`
pega todo diretório de skill automaticamente.

## O que isto NÃO mede

- **Fidelidade** — a resposta comprimida preserva as afirmações
  técnicas? Uma skill que responde `k` pra tudo pontuaria −99% e
  "venceria". Uma v2 futura poderia adicionar uma rubrica de modelo juiz.
- **Latência ou custo** — fora de escopo. Note que skills adicionam tokens
  de entrada em toda chamada, então economia de saída não é o quadro
  econômico completo.
- **Comportamento cross-model** — só o modelo usado pra gerar o
  snapshot é medido.
- **Tokens exatos do Claude** — `tiktoken o200k_base` é BPE da OpenAI e é
  só uma aproximação do tokenizer do Claude. Razões entre braços são
  significativas; números absolutos são aproximados.
- **Significância estatística** — rodada única por (prompt, braço) em
  temperatura padrão. As colunas min/max/stdev te deixam olhar se um
  número é sólido ou ruidoso, mas isto não é um experimento controlado.
