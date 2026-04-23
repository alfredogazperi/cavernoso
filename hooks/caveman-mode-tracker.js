#!/usr/bin/env node
// cavernoso — UserPromptSubmit hook to track which cavernoso mode is active
// Inspects user input for /cavernoso commands and writes mode to flag file

const fs = require('fs');
const path = require('path');
const os = require('os');
const { getDefaultMode, safeWriteFlag, readFlag } = require('./caveman-config');

const claudeDir = process.env.CLAUDE_CONFIG_DIR || path.join(os.homedir(), '.claude');
const flagPath = path.join(claudeDir, '.caveman-active');

let input = '';
process.stdin.on('data', chunk => { input += chunk; });
process.stdin.on('end', () => {
  try {
    const data = JSON.parse(input);
    const prompt = (data.prompt || '').trim().toLowerCase();

    // Natural language activation — pt-BR only (foco do fork).
    // pt-BR: "ativa cavernoso", "liga modo cavernoso", "fala como cavernoso", "modo cavernoso"
    const PT_DEACTIVATE = /\b(para|parar|desliga|desligar|desativa|desativar|sai do modo)\b/i;
    const PT_ACTIVATE = /\b(ativa|ativar|liga|ligar|fala como|falar como|entra no modo)\b.*\bcavernoso\b/i;
    const PT_ACTIVATE_REV = /\bcavernoso\b.*\b(modo|ativa|ativar|liga|ligar)\b/i;
    const PT_MODO_CAVERNOSO = /\bmodo cavernoso\b/i;

    if ((PT_ACTIVATE.test(prompt) || PT_ACTIVATE_REV.test(prompt) || PT_MODO_CAVERNOSO.test(prompt))
        && !PT_DEACTIVATE.test(prompt)) {
      const mode = getDefaultMode();
      if (mode !== 'off') {
        safeWriteFlag(flagPath, mode);
      }
    }

    // Match /cavernoso commands
    if (prompt.startsWith('/cavernoso')) {
      const parts = prompt.split(/\s+/);
      const cmd = parts[0]; // /cavernoso, /cavernoso-commit, /cavernoso-review, etc.
      const arg = parts[1] || '';

      let mode = null;

      if (cmd === '/cavernoso-commit') {
        mode = 'commit';
      } else if (cmd === '/cavernoso-review') {
        mode = 'review';
      } else if (cmd === '/cavernoso-compress' || cmd === '/cavernoso:compress' || cmd === '/cavernoso:cavernoso-compress') {
        mode = 'compress';
      } else if (cmd === '/cavernoso' || cmd === '/cavernoso:cavernoso') {
        if (arg === 'leve') mode = 'leve';
        else if (arg === 'total') mode = 'total';
        else if (arg === 'ultra') mode = 'ultra';
        else mode = getDefaultMode();
      }

      if (mode && mode !== 'off') {
        safeWriteFlag(flagPath, mode);
      } else if (mode === 'off') {
        try { fs.unlinkSync(flagPath); } catch (e) {}
      }
    }

    // Detect deactivation — pt-BR natural language.
    // Triggers: "para", "para cavernoso", "desliga", "desliga cavernoso",
    // "desativa cavernoso", "modo normal", "sai do modo cavernoso".
    if (/\b(para|parar|desliga|desligar|desativa|desativar|sai do modo)\b.*\bcavernoso\b/i.test(prompt) ||
        /\bcavernoso\b.*\b(para|parar|desliga|desligar|desativa|desativar)\b/i.test(prompt) ||
        /\bmodo normal\b/i.test(prompt) ||
        /^\s*para\s*$/i.test(prompt)) {
      try { fs.unlinkSync(flagPath); } catch (e) {}
    }

    // Per-turn reinforcement: emit a structured reminder when cavernoso is active.
    // The SessionStart hook injects the full ruleset once, but models lose it
    // when other plugins inject competing style instructions every turn.
    // This keeps cavernoso visible in the model's attention on every user message.
    //
    // Skip independent modes (commit, review, compress) — they have their own
    // skill behavior and the base cavernoso rules would conflict.
    // readFlag enforces symlink-safe read + size cap + VALID_MODES whitelist.
    // If the flag is missing, corrupted, oversized, or a symlink pointing at
    // something like ~/.ssh/id_rsa, readFlag returns null and we emit nothing
    // — never inject untrusted bytes into model context.
    const INDEPENDENT_MODES = new Set(['commit', 'review', 'compress']);
    const activeMode = readFlag(flagPath);
    if (activeMode && !INDEPENDENT_MODES.has(activeMode)) {
      process.stdout.write(JSON.stringify({
        hookSpecificOutput: {
          hookEventName: "UserPromptSubmit",
          additionalContext: "MODO CAVERNOSO ATIVO (" + activeMode + "). " +
            "Cortar artigos/filler/cortesias/hedging. Fragmentos OK. " +
            "Código/commits/segurança: escrever normal."
        }
      }));
    }
  } catch (e) {
    // Silent fail
  }
});
