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
    //
    // Detecção de desativação aqui é estrita pra não casar com "para" preposição
    // (comum: "configurar X para Y", "para toda sessão"). Ver PT_DEACTIVATE_STRICT
    // abaixo — só "parar", "desliga*", "desativa*", "sai do modo", ou "para" verbo
    // seguido direto de "cavernoso" (com "o" opcional).
    const PT_DEACTIVATE_STRICT = /(?:^|[,.:;!?]\s*)para\s+(?:o\s+)?cavernoso\b|\b(parar|desliga(?:r)?|desativa(?:r)?|sai do modo)\b.*\bcavernoso\b|\bcavernoso\b[\s,.:;!?-]*\b(parar|desliga(?:r)?|desativa(?:r)?)\b|\bcavernoso\b[\s,.:;!?-]*\bpara(?=[\s,.:;!?-]*$)|\bmodo normal\b|^\s*para\s*$/i;
    const PT_ACTIVATE = /\b(ativa|ativar|liga|ligar|fala como|falar como|entra no modo)\b.*\bcavernoso\b/i;
    const PT_ACTIVATE_REV = /\bcavernoso\b.*\b(modo|ativa|ativar|liga|ligar)\b/i;
    const PT_MODO_CAVERNOSO = /\bmodo cavernoso\b/i;

    if ((PT_ACTIVATE.test(prompt) || PT_ACTIVATE_REV.test(prompt) || PT_MODO_CAVERNOSO.test(prompt))
        && !PT_DEACTIVATE_STRICT.test(prompt)) {
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
    // Triggers: "para cavernoso", "parar cavernoso", "desliga cavernoso",
    // "desativa cavernoso", "modo normal", "sai do modo cavernoso",
    // ou só "para" isolado.
    //
    // ATENÇÃO: "para" preposição é altamente frequente em pt-BR ("para toda
    // sessão", "configurar para que", "para ativar X"). Regex exige:
    //   (a) verbo de desativação + "cavernoso" como complemento direto, OU
    //   (b) "cavernoso" + verbo de desativação logo depois, OU
    //   (c) "modo normal" explícito, OU
    //   (d) prompt inteiro sendo literalmente "para".
    //
    // Para evitar falso positivo de "para" preposição ("para toda sessão iniciar
    // no modo cavernoso"), só conta "para" como verbo de desativação quando
    // vem IMEDIATAMENTE antes de "cavernoso" (com artigo "o" opcional).
    // Verbos inequívocos ("parar", "desliga*", "desativa*") mantêm o padrão
    // "verbo ... cavernoso" mais permissivo.
    // "para cavernoso" / "para o cavernoso" — imperativo, desativa.
    const PARA_DESATIVA = /(?:^|[,.:;!?]\s*)para\s+(?:o\s+)?cavernoso\b/i;
    // "parar cavernoso" / "desliga cavernoso" / etc. — verbos inequívocos.
    const VERBO_DESATIVA_CAVERNOSO = /\b(parar|desliga(?:r)?|desativa(?:r)?|sai do modo)\b.*\bcavernoso\b/i;
    // "cavernoso para" / "cavernoso, para." — "para" ambíguo, só conta se for fim de frase
    // (pontuação terminal ou fim da string). "cavernoso para toda sessão" NÃO casa.
    const CAVERNOSO_PARA_FIM = /\bcavernoso\b[\s,.:;!?-]*\bpara(?=[\s,.:;!?-]*$)/i;
    // "cavernoso desliga" / "cavernoso, desativa" — verbos inequívocos, direto após cavernoso.
    const CAVERNOSO_VERBO_DESATIVA = /\bcavernoso\b[\s,.:;!?-]*\b(parar|desliga(?:r)?|desativa(?:r)?)\b/i;
    if (PARA_DESATIVA.test(prompt) ||
        VERBO_DESATIVA_CAVERNOSO.test(prompt) ||
        CAVERNOSO_VERBO_DESATIVA.test(prompt) ||
        CAVERNOSO_PARA_FIM.test(prompt) ||
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
