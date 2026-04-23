# Hooks do Cavernoso

Estes hooks são **distribuídos com o plugin cavernoso** e ativam automaticamente quando o plugin é instalado. Nenhuma configuração manual necessária.

Se você instalou cavernoso standalone (sem o plugin), pode usar `bash hooks/install.sh` para conectá-los manualmente no seu settings.json.

> Nota: os arquivos dos hooks ainda mantêm o prefixo `caveman-` no nome (`caveman-activate.js`, `caveman-mode-tracker.js`, `caveman-statusline.sh`) porque são referenciados por path no `plugin.json`. Comportamento e mensagens internas são `cavernoso`.

## O que está incluído

### `caveman-activate.js` — hook SessionStart

- Roda uma vez quando o Claude Code inicia
- Escreve `total` em `~/.claude/.caveman-active` (arquivo de flag)
- Emite regras do cavernoso como contexto oculto de SessionStart
- Detecta config de statusline ausente e emite cutucada de setup (Claude vai oferecer ajuda)

### `caveman-mode-tracker.js` — hook UserPromptSubmit

- Dispara em todo prompt do usuário, checa por comandos `/cavernoso`
- Escreve o modo ativo no arquivo de flag quando um comando cavernoso é detectado
- Suporta: `leve`, `total`, `ultra`, `commit`, `review`, `compress`

### `caveman-statusline.sh` / `caveman-statusline.ps1` — script de badge de statusline

- Lê `~/.claude/.caveman-active` e imprime um badge colorido
- Mostra `[CAVERNOSO]`, `[CAVERNOSO:ULTRA]`, etc.

## Badge de Statusline

O badge de statusline mostra qual modo do cavernoso está ativo diretamente na barra de status do Claude Code.

**Usuários de plugin:** Se você ainda não tem `statusLine` configurado, Claude detecta isso na sua primeira sessão após o install e oferece configurar pra você. Aceite e pronto.

Se você já tem um statusline customizado, cavernoso não sobrescreve e Claude fica quieto. Em vez disso, adicione o snippet do badge ao seu script existente.

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
cavernoso_text=""
cavernoso_flag="$HOME/.claude/.caveman-active"
if [ -f "$cavernoso_flag" ]; then
  cavernoso_mode=$(cat "$cavernoso_flag" 2>/dev/null)
  if [ "$cavernoso_mode" = "total" ] || [ -z "$cavernoso_mode" ]; then
    cavernoso_text=$'\033[38;5;172m[CAVERNOSO]\033[0m'
  else
    cavernoso_suffix=$(echo "$cavernoso_mode" | tr '[:lower:]' '[:upper:]')
    cavernoso_text=$'\033[38;5;172m[CAVERNOSO:'"${cavernoso_suffix}"$']\033[0m'
  fi
fi
```

Exemplos de badge:
- `/cavernoso` → `[CAVERNOSO]`
- `/cavernoso ultra` → `[CAVERNOSO:ULTRA]`
- `/cavernoso-commit` → `[CAVERNOSO:COMMIT]`
- `/cavernoso-review` → `[CAVERNOSO:REVIEW]`

## Como funciona

```
hook SessionStart ──escreve "total"──▶ ~/.claude/.caveman-active ◀──escreve modo── hook UserPromptSubmit
                                              │
                                             lê
                                              ▼
                                     Script de statusline
                                    [CAVERNOSO:ULTRA] │ ...
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
