#!/usr/bin/env python3
"""
Caveman Memory Compression Orchestrator

Usage:
    python scripts/compress.py <filepath>
"""

import os
import re
import subprocess
from pathlib import Path
from typing import List

try:
    from .preprocess import preprocess as pt_preprocess
except ImportError:  # quando rodado como script direto
    from preprocess import preprocess as pt_preprocess  # type: ignore

OUTER_FENCE_REGEX = re.compile(
    r"\A\s*(`{3,}|~{3,})[^\n]*\n(.*)\n\1\s*\Z", re.DOTALL
)

# Filenames and paths that almost certainly hold secrets or PII. Compressing
# them ships raw bytes to the Anthropic API — a third-party data boundary that
# developers on sensitive codebases cannot cross. detect.py already skips .env
# by extension, but credentials.md / secrets.txt / ~/.aws/credentials would
# slip through the natural-language filter. This is a hard refuse before read.
SENSITIVE_BASENAME_REGEX = re.compile(
    r"(?ix)^("
    r"\.env(\..+)?"
    r"|\.netrc"
    r"|credentials(\..+)?"
    r"|secrets?(\..+)?"
    r"|passwords?(\..+)?"
    r"|id_(rsa|dsa|ecdsa|ed25519)(\.pub)?"
    r"|authorized_keys"
    r"|known_hosts"
    r"|.*\.(pem|key|p12|pfx|crt|cer|jks|keystore|asc|gpg)"
    r")$"
)

SENSITIVE_PATH_COMPONENTS = frozenset({".ssh", ".aws", ".gnupg", ".kube", ".docker"})

SENSITIVE_NAME_TOKENS = (
    "secret", "credential", "password", "passwd",
    "apikey", "accesskey", "token", "privatekey",
)


def is_sensitive_path(filepath: Path) -> bool:
    """Heuristic denylist for files that must never be shipped to a third-party API."""
    name = filepath.name
    if SENSITIVE_BASENAME_REGEX.match(name):
        return True
    lowered_parts = {p.lower() for p in filepath.parts}
    if lowered_parts & SENSITIVE_PATH_COMPONENTS:
        return True
    # Normalize separators so "api-key" and "api_key" both match "apikey".
    lower = re.sub(r"[_\-\s.]", "", name.lower())
    return any(tok in lower for tok in SENSITIVE_NAME_TOKENS)


def strip_llm_wrapper(text: str) -> str:
    """Strip outer ```markdown ... ``` fence when it wraps the entire output."""
    m = OUTER_FENCE_REGEX.match(text)
    if m:
        return m.group(2)
    return text

from .detect import should_compress
from .validate import validate

MAX_RETRIES = 2


# ---------- Claude Calls ----------


def call_claude(prompt: str) -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        try:
            import anthropic

            client = anthropic.Anthropic(api_key=api_key)
            msg = client.messages.create(
                model=os.environ.get("CAVEMAN_MODEL", "claude-sonnet-4-5"),
                max_tokens=8192,
                messages=[{"role": "user", "content": prompt}],
            )
            return strip_llm_wrapper(msg.content[0].text.strip())
        except ImportError:
            pass  # anthropic not installed, fall back to CLI
    # Fallback: use claude CLI (handles desktop auth)
    try:
        result = subprocess.run(
            ["claude", "--print"],
            input=prompt,
            text=True,
            capture_output=True,
            check=True,
        )
        return strip_llm_wrapper(result.stdout.strip())
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Claude call failed:\n{e.stderr}")


def build_compress_prompt(original: str) -> str:
    return f"""
Comprimir este markdown para o formato cavernoso em português brasileiro (pt-BR).

IDIOMA:
- Saída DEVE permanecer em português. NÃO traduzir para inglês.
- Manter termos técnicos em inglês quando forem jargão estabelecido: push, pull, commit, merge, deploy, build, release, rollback, branch, tag, issue, PR, runtime, stack, framework, endpoint, payload, request, response, bug, fix, hook, trigger, callback, pipeline.

REGRAS ESTRITAS:
- NÃO modificar nada dentro de blocos de código ```
- NÃO modificar nada dentro de crases inline `...`
- Preservar TODAS as URLs exatamente
- Preservar TODOS os cabeçalhos exatamente
- Preservar caminhos de arquivos e comandos
- Retornar APENAS o corpo do markdown comprimido — NÃO envolver a saída em ```markdown ou outra cerca. Blocos de código internos ficam como estão; não adicionar nova cerca externa.

COMPRIMIR apenas linguagem natural. Remover:

- Artigos definidos e indefinidos quando possível: "o", "a", "os", "as", "um", "uma", "uns", "umas"
- Filler: "basicamente", "simplesmente", "na verdade", "efetivamente", "literalmente", "realmente", "praticamente", "obviamente", "claramente", "meio que", "tipo", "então" (quando filler), "enfim"
- Cortesias: "com certeza", "claro", "sem dúvida", "fico feliz em", "recomendo que", "sugiro que"
- Hedging: "talvez seja interessante", "vale a pena considerar", "seria bom", "pode ser que", "eu acho que"
- Fluff conectivo: "além disso", "ademais", "entretanto", "todavia", "outrossim", "dessa forma", "sendo assim", "nesse sentido", "dito isso"
- Redundâncias: "de forma a" → "para", "no sentido de" → "para", "pelo fato de que" → "porque", "tendo em vista que" → "pois", "em virtude de" → "por"
- Expressões vazias: "é importante notar que", "vale a pena mencionar que", "cabe ressaltar que", "no momento atual", "considerando tudo"

PREFERIR SINÔNIMOS CURTOS:
- "usar" em vez de "utilizar"
- "fazer" em vez de "realizar"
- "ver" em vez de "visualizar"
- "achar" em vez de "encontrar" (em contextos informais)
- "criar" em vez de "desenvolver" quando possível
- "grande" em vez de "extenso"

FRAGMENTOS OK. Gramática completa não é obrigatória. Imperativo direto.
Cortar "você deve", "certifique-se de", "lembre-se de" — só afirmar a ação.

EXEMPLO:
Original: "Você deve sempre se certificar de rodar os testes antes de fazer push para a branch main. Isso é importante porque ajuda a pegar bugs cedo."
Comprimido: "Rodar testes antes de push para main. Pega bugs cedo."

Lembrete: saída em português pt-BR.

TEXTO:
{original}
"""


def build_fix_prompt(original: str, compressed: str, errors: List[str]) -> str:
    errors_str = "\n".join(f"- {e}" for e in errors)
    return f"""Você está corrigindo um arquivo markdown comprimido no formato cavernoso pt-BR. Erros específicos de validação foram encontrados.

REGRAS CRÍTICAS:
- NÃO recomprimir ou reformular o arquivo
- APENAS corrigir os erros listados — deixar todo o resto exatamente como está
- O ORIGINAL é fornecido só como referência (para restaurar conteúdo faltante)
- Preservar o estilo cavernoso em todas as seções não tocadas
- Saída em português pt-BR

ERROS A CORRIGIR:
{errors_str}

COMO CORRIGIR:
- URL faltante: achar no ORIGINAL, restaurar exato onde pertence no COMPRIMIDO
- Bloco de código divergente: achar o bloco exato no ORIGINAL, restaurar no COMPRIMIDO
- Cabeçalho divergente: restaurar texto exato do cabeçalho do ORIGINAL no COMPRIMIDO
- Não mexer em nenhuma seção não mencionada nos erros

ORIGINAL (só referência):
{original}

COMPRIMIDO (corrigir este):
{compressed}

Retornar APENAS o arquivo comprimido corrigido. Sem explicação.
"""


# ---------- Core Logic ----------


def compress_file(filepath: Path) -> bool:
    # Resolve and validate path
    filepath = filepath.resolve()
    MAX_FILE_SIZE = 500_000  # 500KB
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    if filepath.stat().st_size > MAX_FILE_SIZE:
        raise ValueError(f"File too large to compress safely (max 500KB): {filepath}")

    # Refuse files that look like they contain secrets or PII. Compressing ships
    # the raw bytes to the Anthropic API — a third-party boundary — so we fail
    # loudly rather than silently exfiltrate credentials or keys. Override is
    # intentional: the user must rename the file if the heuristic is wrong.
    if is_sensitive_path(filepath):
        raise ValueError(
            f"Refusing to compress {filepath}: filename looks sensitive "
            "(credentials, keys, secrets, or known private paths). "
            "Compression sends file contents to the Anthropic API. "
            "Rename the file if this is a false positive."
        )

    print(f"Processing: {filepath}")

    if not should_compress(filepath):
        print("Skipping (not natural language)")
        return False

    original_text = filepath.read_text(errors="ignore")
    backup_path = filepath.with_name(filepath.stem + ".original.md")

    # Check if backup already exists to prevent accidental overwriting
    if backup_path.exists():
        print(f"⚠️ Backup file already exists: {backup_path}")
        print("The original backup may contain important content.")
        print("Aborting to prevent data loss. Please remove or rename the backup file if you want to proceed.")
        return False

    # Step 1a: Deterministic pt-BR preprocess (removes fixed redundancies,
    # pleonasms, empty phrases, and isolated filler before LLM call).
    preprocessed_text = pt_preprocess(original_text)
    if preprocessed_text != original_text:
        pre_saved = len(original_text) - len(preprocessed_text)
        print(f"Pré-processamento pt-BR removeu {pre_saved} chars antes do LLM.")

    # Step 1b: Compress via Claude
    print("Comprimindo com Claude...")
    compressed = call_claude(build_compress_prompt(preprocessed_text))

    # Save original as backup, write compressed to original path
    backup_path.write_text(original_text)
    filepath.write_text(compressed)

    # Step 2: Validate + Retry
    for attempt in range(MAX_RETRIES):
        print(f"\nValidation attempt {attempt + 1}")

        result = validate(backup_path, filepath)

        if result.is_valid:
            print("Validation passed")
            break

        print("❌ Validation failed:")
        for err in result.errors:
            print(f"   - {err}")

        if attempt == MAX_RETRIES - 1:
            # Restore original on failure
            filepath.write_text(original_text)
            backup_path.unlink(missing_ok=True)
            print("❌ Failed after retries — original restored")
            return False

        print("Fixing with Claude...")
        compressed = call_claude(
            build_fix_prompt(original_text, compressed, result.errors)
        )
        filepath.write_text(compressed)

    return True
