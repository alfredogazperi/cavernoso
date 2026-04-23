"""
Pré-processamento determinístico pt-BR para caveman-compress.

Roda antes da chamada ao LLM. Aplica substituições e remoções seguras
(sem ambiguidade) que economizam tokens na entrada do Claude:

1. Redundâncias fixas: "de forma a" → "para", "pelo fato de que" → "porque", ...
2. Pleonasmos comuns: "subir para cima" → "subir", "entrar para dentro" → "entrar", ...
3. Filler determinístico fora de contexto: "basicamente,", "simplesmente,", "na verdade,", ...
4. Expressões vazias: "é importante notar que", "vale a pena mencionar que", ...

Regras de proteção — NUNCA tocar:
- Blocos de código cercados (``` ... ```) e indentados (4 espaços / tab)
- Código inline (`...`)
- URLs (http, https, markdown links)
- Caminhos de arquivo
- Frontmatter YAML no topo

Estratégia: extrair regiões protegidas, substituir por sentinelas, rodar transformações
na prosa, depois restaurar as regiões.
"""

from __future__ import annotations

import re
from typing import List, Tuple


# ----------------------------------------------------------------------
# Listas de substituição
# ----------------------------------------------------------------------

# Redundâncias — (pattern regex, replacement). Case-insensitive.
REDUNDANCIAS: List[Tuple[str, str]] = [
    (r"\bde forma a\b", "para"),
    (r"\bno sentido de\b", "para"),
    (r"\bcom o objetivo de\b", "para"),
    (r"\bcom o intuito de\b", "para"),
    (r"\bcom a finalidade de\b", "para"),
    (r"\bpelo fato de que\b", "porque"),
    (r"\btendo em vista que\b", "pois"),
    (r"\bdevido ao fato de que\b", "porque"),
    (r"\bem virtude de\b", "por"),
    (r"\bno caso de\b", "se"),
    (r"\bna maior parte\b", "geralmente"),
    (r"\bnão obstante\b", "mas"),
    (r"\bapesar do fato de que\b", "embora"),
    (r"\bao mesmo tempo em que\b", "enquanto"),
    (r"\bpor meio de\b", "por"),
    (r"\batravés de\b", "por"),
    (r"\b(faz|fazer)(-se)? necessário\b", r"precisa"),
]

# Pleonasmos brasileiros clássicos — sempre seguros de remover.
PLEONASMOS: List[Tuple[str, str]] = [
    (r"\bsubir para cima\b", "subir"),
    (r"\bdescer para baixo\b", "descer"),
    (r"\bentrar para dentro\b", "entrar"),
    (r"\bsair para fora\b", "sair"),
    (r"\bencarar de frente\b", "encarar"),
    (r"\bcriar novo?\b", "criar"),
    (r"\b(elo|planejar) de antemão\b", r"\1"),
    (r"\bplanejar antecipadamente\b", "planejar"),
    (r"\bpreview antecipado\b", "preview"),
    (r"\bconclusão final\b", "conclusão"),
    (r"\bpergunta feita\b", "pergunta"),
    (r"\bsurpresa inesperada\b", "surpresa"),
    (r"\brepetir de novo\b", "repetir"),
    (r"\bmas porém\b", "mas"),
    (r"\bmonopólio exclusivo\b", "monopólio"),
    (r"\bhemorragia de sangue\b", "hemorragia"),
    (r"\bcanja de galinha\b", "canja"),  # ok no Brasil, mas tecnicamente pleonástico
    (r"\belo entre\b", "entre"),
    (r"\bsorriso nos lábios\b", "sorriso"),
    (r"\bhá tempos atrás\b", "há tempos"),
    (r"\bfaz tempo atrás\b", "faz tempo"),
]

# Expressões vazias — remover completamente (seguidas de vírgula ou no início de frase).
EXPRESSOES_VAZIAS: List[str] = [
    r"é importante notar que",
    r"é importante ressaltar que",
    r"é importante mencionar que",
    r"vale a pena notar que",
    r"vale a pena mencionar que",
    r"vale a pena ressaltar que",
    r"cabe ressaltar que",
    r"cabe mencionar que",
    r"é digno de nota que",
    r"é necessário lembrar que",
    r"como mencionado anteriormente,?",
    r"conforme exposto acima,?",
    r"tendo em vista o exposto,?",
    r"dito isso,?",
    r"nesse sentido,?",
    r"no momento atual,?",
    r"considerando tudo,?",
    r"o que quero dizer é que",
    r"parece que",
    r"de fato,?",
]

# Filler — remove quando isolado por pontuação/espaço (não quebra significado).
FILLER_ISOLADO: List[str] = [
    r"basicamente",
    r"simplesmente",
    r"na verdade",
    r"efetivamente",
    r"literalmente",
    r"realmente",
    r"praticamente",
    r"obviamente",
    r"claramente",
    r"definitivamente",
    r"enfim",
    r"comumente",
    r"totalmente",
]


# ----------------------------------------------------------------------
# Proteção de regiões
# ----------------------------------------------------------------------

# Sentinela improvável de aparecer em texto real.
_SENTINEL = "§§CVN{}§§"

# Regexes para regiões protegidas (aplicadas em ordem).
_PROTECTED_PATTERNS = [
    # Frontmatter YAML no topo do arquivo
    (re.compile(r"\A---\n.*?\n---\n", re.DOTALL), "frontmatter"),
    # Blocos de código cercados ```
    (re.compile(r"```[\s\S]*?```", re.MULTILINE), "fence"),
    # Tabelas pipe-separated (linhas com | no começo, preserva formato)
    (re.compile(r"(^\|[^\n]*\|\s*\n)+", re.MULTILINE), "table"),
    # Código inline `...`
    (re.compile(r"`[^`\n]+`"), "inline"),
    # URLs markdown [texto](url)
    (re.compile(r"\[[^\]]*\]\([^)]+\)"), "mdlink"),
    # URLs soltas
    (re.compile(r"https?://[^\s<>\"']+"), "url"),
    # Caminhos absolutos (/foo/bar) e relativos (./foo, ../foo)
    (re.compile(r"(?<![\w])(?:\.\.?/|/)[\w\-./]+"), "path"),
]


def _protect(text: str) -> Tuple[str, List[str]]:
    """Extrai regiões protegidas, substitui por sentinelas. Retorna (texto_modificado, lista_regiões)."""
    regions: List[str] = []

    def replace(m: re.Match) -> str:
        regions.append(m.group(0))
        return _SENTINEL.format(len(regions) - 1)

    for pattern, _name in _PROTECTED_PATTERNS:
        text = pattern.sub(replace, text)

    return text, regions


def _restore(text: str, regions: List[str]) -> str:
    """Restaura regiões protegidas em ordem inversa para evitar colisão de índices."""
    for i in range(len(regions) - 1, -1, -1):
        text = text.replace(_SENTINEL.format(i), regions[i])
    return text


# ----------------------------------------------------------------------
# Transformações
# ----------------------------------------------------------------------


def _apply_replacements(text: str, pairs: List[Tuple[str, str]]) -> str:
    for pattern, repl in pairs:
        text = re.sub(pattern, repl, text, flags=re.IGNORECASE)
    return text


def _remove_expressoes_vazias(text: str) -> str:
    for phrase in EXPRESSOES_VAZIAS:
        # Remove com o espaço seguinte para não deixar duplo espaço.
        text = re.sub(rf"\b{phrase}\s*", "", text, flags=re.IGNORECASE)
    return text


def _remove_filler_isolado(text: str) -> str:
    """Remove filler quando seguido de vírgula ou ponto (marcador claro de não-essencial)."""
    for word in FILLER_ISOLADO:
        # Remove "basicamente," / "basicamente." preservando pontuação.
        text = re.sub(rf"\b{word}\b,\s*", "", text, flags=re.IGNORECASE)
        # Remove quando começa sentença: ". Basicamente " → ". "
        text = re.sub(rf"(?<=[.!?])\s+{word}\b\s*", " ", text, flags=re.IGNORECASE)
    return text


def _cleanup_whitespace(text: str) -> str:
    """Remove múltiplos espaços, pontuação órfã e linhas em branco excessivas."""
    # Múltiplos espaços → um
    text = re.sub(r"[ \t]{2,}", " ", text)
    # Espaço antes de pontuação
    text = re.sub(r"\s+([.,;:!?])", r"\1", text)
    # Pontuação órfã no início de linha (deixada por remoções)
    text = re.sub(r"(^|\n)\s*[,;:]+\s*", r"\1", text)
    # Três ou mais quebras de linha → duas
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Capitalizar primeira letra depois de ponto (bonus de limpeza)
    return text


# ----------------------------------------------------------------------
# API pública
# ----------------------------------------------------------------------


def preprocess(text: str) -> str:
    """
    Aplica pré-processamento determinístico pt-BR.

    Proteção: código, URLs, caminhos, frontmatter e tabelas são extraídos,
    transformações rodam só na prosa, e as regiões são restauradas intactas.
    """
    protected, regions = _protect(text)

    protected = _apply_replacements(protected, REDUNDANCIAS)
    protected = _apply_replacements(protected, PLEONASMOS)
    protected = _remove_expressoes_vazias(protected)
    protected = _remove_filler_isolado(protected)
    protected = _cleanup_whitespace(protected)

    return _restore(protected, regions)


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Uso: python -m scripts.preprocess <arquivo>", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]
    with open(path, "r", encoding="utf-8") as f:
        original = f.read()

    result = preprocess(original)
    orig_chars = len(original)
    new_chars = len(result)
    reduction = (1 - new_chars / orig_chars) * 100 if orig_chars else 0
    print(result)
    print(
        f"\n--- pré-processamento: {orig_chars} → {new_chars} chars "
        f"({reduction:.1f}% redução determinística) ---",
        file=sys.stderr,
    )
