# Hooks do Caveman

Estes hooks são **distribuídos com o plugin caveman** e ativam automaticamente quando o plugin é instalado. Nenhuma configuração manual necessária.

Se você instalou caveman standalone (sem o plugin), pode usar `bash hooks/install.sh` para conectá-los manualmente no seu settings.json.

## O que está incluído

### `caveman-activate.js` — hook SessionStart

- Roda uma vez quando o Claude Code inicia
- Escreve `full` em `~/.claude/.caveman-active` (arquivo de flag)
- Emite regras do caveman como contexto oculto de SessionStart
- Detecta config de statusline ausente e emite cutucada de setup (Claude vai oferecer ajuda)

### `caveman-mode-tracker.js` — hook UserPromptSubmit

- Dispara em todo prompt do usuário, checa por comandos `/caveman`
- Escreve o modo ativo no arquivo de flag quando um comando caveman é detectado
- Suporta: `full`, `lite`, `ultra`, `commit`, `review`, `compress`

### `caveman-statusline.sh` / `caveman-statusline.ps1` — script de badge de statusline

- Lê `~/.claude/.caveman-active` e imprime um badge colorido
- Mostra `[CAVEMAN]`, `[CAVEMAN:ULTRA]`, etc.

## Badge de Statusline

O badge de statusline mostra qual modo do caveman está ativo diretamente na barra de status do Claude Code.

**Usuários de plugin:** Se você ainda não tem `statusLine` configurado, Claude detecta isso na sua primeira sessão após o install e oferece configurar pra você. Aceite e pronto.

Se você já tem um statusline customizado, caveman não sobrescreve e Claude fica quieto. Em vez disso, adicione o snippet do badge ao seu script existente.

**Usuários standalone:** `install.sh` / `install.ps1` conecta o statusline automaticamente se você ainda não tem um customizado. Se tem, o instalador deixa em paz e imprime a nota de merge.

**Setup manual:** Se precisa configurar você mesmo, adicione um destes ao `~/.claude/settings.json`:

```json
{
  "statusLine": {
    "type": "command",
    "command": "bash /path/to/caveman-statusline.sh"
  }
}
```

```json
{
  "statusLine": {
    "type": "command",
    "command": "powershell -ExecutionPolicy Bypass -File C:\\path\\to\\caveman-statusline.ps1"
  }
}
```

Substitua o caminho pela localização real do script (ex.: `~/.claude/hooks/` para installs standalone, ou o diretório de install do plugin para installs via plugin).

**Statusline customizado:** Se você já tem um script de statusline, adicione este snippet nele:

```bash
caveman_text=""
caveman_flag="$HOME/.claude/.caveman-active"
if [ -f "$caveman_flag" ]; then
  caveman_mode=$(cat "$caveman_flag" 2>/dev/null)
  if [ "$caveman_mode" = "full" ] || [ -z "$caveman_mode" ]; then
    caveman_text=$'\033[38;5;172m[CAVEMAN]\033[0m'
  else
    caveman_suffix=$(echo "$caveman_mode" | tr '[:lower:]' '[:upper:]')
    caveman_text=$'\033[38;5;172m[CAVEMAN:'"${caveman_suffix}"$']\033[0m'
  fi
fi
```

Exemplos de badge:
- `/caveman` → `[CAVEMAN]`
- `/caveman ultra` → `[CAVEMAN:ULTRA]`
- `/caveman-commit` → `[CAVEMAN:COMMIT]`
- `/caveman-review` → `[CAVEMAN:REVIEW]`

## Como funciona

```
hook SessionStart ──escreve "full"──▶ ~/.claude/.caveman-active ◀──escreve modo── hook UserPromptSubmit
                                              │
                                             lê
                                              ▼
                                     Script de statusline
                                    [CAVEMAN:ULTRA] │ ...
```

Stdout do SessionStart é injetado como contexto de sistema oculto — Claude vê, usuários não. O statusline roda como processo separado. O arquivo de flag é a ponte.

## Desinstalar

Se instalado via plugin: desabilite o plugin — hooks desativam automaticamente.

Se instalado via `install.sh`:
```bash
bash hooks/uninstall.sh
```

Ou manualmente:
1. Remova `~/.claude/hooks/caveman-activate.js`, `~/.claude/hooks/caveman-mode-tracker.js`, e o script de statusline correspondente (`caveman-statusline.sh` no macOS/Linux ou `caveman-statusline.ps1` no Windows)
2. Remova as entradas SessionStart, UserPromptSubmit e statusLine do `~/.claude/settings.json`
3. Delete `~/.claude/.caveman-active`
