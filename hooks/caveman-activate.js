#!/usr/bin/env node
// caveman — Claude Code SessionStart activation hook
//
// Runs on every session start:
//   1. Writes flag file at $CLAUDE_CONFIG_DIR/.caveman-active (statusline reads this)
//   2. Emits caveman ruleset as hidden SessionStart context
//   3. Detects missing statusline config and emits setup nudge

const fs = require('fs');
const path = require('path');
const os = require('os');
const { getDefaultMode, safeWriteFlag } = require('./caveman-config');

const claudeDir = process.env.CLAUDE_CONFIG_DIR || path.join(os.homedir(), '.claude');
const flagPath = path.join(claudeDir, '.caveman-active');
const settingsPath = path.join(claudeDir, 'settings.json');

const mode = getDefaultMode();

// "off" mode — skip activation entirely, don't write flag or emit rules
if (mode === 'off') {
  try { fs.unlinkSync(flagPath); } catch (e) {}
  process.stdout.write('OK');
  process.exit(0);
}

// 1. Write flag file (symlink-safe)
safeWriteFlag(flagPath, mode);

// 2. Emit full caveman ruleset, filtered to the active intensity level.
//    The old 2-sentence summary was too weak — models drifted back to verbose
//    mid-conversation, especially after context compression pruned it away.
//    Full rules with examples anchor behavior much more reliably.
//
//    Reads SKILL.md at runtime so edits to the source of truth propagate
//    automatically — no hardcoded duplication to go stale.

// Modes that have their own independent skill files — not caveman intensity levels.
// For these, emit a short activation line; the skill itself handles behavior.
const INDEPENDENT_MODES = new Set(['commit', 'review', 'compress']);

if (INDEPENDENT_MODES.has(mode)) {
  process.stdout.write('MODO CAVERNOSO ATIVO — nível: ' + mode + '. Comportamento definido pela skill /caveman-' + mode + '.');
  process.exit(0);
}

const modeLabel = mode;

// Read SKILL.md — the single source of truth for caveman behavior.
// Plugin installs: __dirname = <plugin_root>/hooks/, SKILL.md at <plugin_root>/skills/caveman/SKILL.md
// Standalone installs: __dirname = $CLAUDE_CONFIG_DIR/hooks/, SKILL.md won't exist — falls back to hardcoded rules.
let skillContent = '';
try {
  skillContent = fs.readFileSync(
    path.join(__dirname, '..', 'skills', 'caveman', 'SKILL.md'), 'utf8'
  );
} catch (e) { /* standalone install — will use fallback below */ }

let output;

if (skillContent) {
  // Strip YAML frontmatter
  const body = skillContent.replace(/^---[\s\S]*?---\s*/, '');

  // Filter intensity table: keep header rows + only the active level's row
  const filtered = body.split('\n').reduce((acc, line) => {
    // Intensity table rows start with | **level** |
    const tableRowMatch = line.match(/^\|\s*\*\*(\S+?)\*\*\s*\|/);
    if (tableRowMatch) {
      // Keep only the active level's row (and always keep header/separator)
      if (tableRowMatch[1] === modeLabel) {
        acc.push(line);
      }
      return acc;
    }

    // Example lines start with "- level:" — keep only lines matching active level
    const exampleMatch = line.match(/^- (\S+?):\s/);
    if (exampleMatch) {
      if (exampleMatch[1] === modeLabel) {
        acc.push(line);
      }
      return acc;
    }

    acc.push(line);
    return acc;
  }, []);

  output = 'MODO CAVERNOSO ATIVO — nível: ' + modeLabel + '\n\n' + filtered.join('\n');
} else {
  // Fallback when SKILL.md is not found (standalone hook install without skills dir).
  // This is the minimum viable ruleset — better than nothing.
  output =
    'MODO CAVERNOSO ATIVO — nível: ' + modeLabel + '\n\n' +
    'Responder seco que nem cavernoso inteligente. Substância técnica fica toda. Só enrolação morre.\n\n' +
    '## Persistência\n\n' +
    'ATIVO TODA RESPOSTA. Não volta depois de muitos turnos. Sem deriva pra enrolação. Continua ativo se incerto. Desliga só: "para cavernoso" / "modo normal".\n\n' +
    'Nível atual: **' + modeLabel + '**. Trocar: `/caveman lite|full|ultra`.\n\n' +
    '## Regras\n\n' +
    'Cortar: artigos (o/a/os/as/um/uma), filler (basicamente/simplesmente/na verdade/literalmente/realmente), cortesias (claro/com certeza/sem dúvida/fico feliz), hedging (talvez/pode ser que/acho que). ' +
    'Fragmentos OK. Sinônimos curtos (usar não utilizar, ver não visualizar, achar não encontrar). Termos técnicos exatos. Blocos de código intocados. Erros citados exato.\n\n' +
    'Padrão: `[coisa] [ação] [motivo]. [próximo passo].`\n\n' +
    'Não: "Com certeza! Fico feliz em ajudar. O problema que você está enfrentando provavelmente é causado por..."\n' +
    'Sim: "Bug no middleware de auth. Checagem de expiração usa `<` não `<=`. Fix:"\n\n' +
    '## Clareza automática\n\n' +
    'Sair do cavernoso pra: avisos de segurança, confirmações de ação irreversível, sequências multi-passo onde ordem de fragmento pode confundir, usuário pede esclarecimento ou repete pergunta. Voltar ao cavernoso depois da parte clara.\n\n' +
    '## Limites\n\n' +
    'Código/commits/PRs: escrever normal. "para cavernoso" ou "modo normal": volta. Nível persiste até mudar ou fim da sessão.';
}

// 3. Detect missing statusline config — nudge Claude to help set it up
try {
  let hasStatusline = false;
  if (fs.existsSync(settingsPath)) {
    const settings = JSON.parse(fs.readFileSync(settingsPath, 'utf8'));
    if (settings.statusLine) {
      hasStatusline = true;
    }
  }

  if (!hasStatusline) {
    const isWindows = process.platform === 'win32';
    const scriptName = isWindows ? 'caveman-statusline.ps1' : 'caveman-statusline.sh';
    const scriptPath = path.join(__dirname, scriptName);
    const command = isWindows
      ? `powershell -ExecutionPolicy Bypass -File "${scriptPath}"`
      : `bash "${scriptPath}"`;
    const statusLineSnippet =
      '"statusLine": { "type": "command", "command": ' + JSON.stringify(command) + ' }';
    output += "\n\n" +
      "STATUSLINE PRECISA SER CONFIGURADA: O plugin cavernoso inclui um badge de statusline mostrando o modo ativo " +
      "(ex.: [CAVERNOSO], [CAVERNOSO:ULTRA]). Ainda não está configurado. " +
      "Para habilitar, adicionar em " + path.join(claudeDir, 'settings.json') + ": " +
      statusLineSnippet + " " +
      "Oferecer proativamente configurar isso pro usuário na primeira interação.";
  }
} catch (e) {
  // Silent fail — don't block session start over statusline detection
}

process.stdout.write(output);
