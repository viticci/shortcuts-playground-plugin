#!/usr/bin/env python3
"""Resolve Shortcuts icon glyph + color from natural language.

Examples:
  python3 scripts/select_shortcut_icon_color.py --prompt "Build a weather shortcut"
  python3 scripts/select_shortcut_icon_color.py --prompt "Expense tracker" --icon "calculator" --color gold
"""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import Any

DEFAULT_GLYPH = 61440  # shortcuts
DEFAULT_COLOR_VALUE = 431817727  # Teal

STOP_WORDS = {
    "a",
    "an",
    "and",
    "app",
    "as",
    "be",
    "build",
    "by",
    "create",
    "for",
    "from",
    "i",
    "icon",
    "in",
    "is",
    "it",
    "make",
    "my",
    "of",
    "on",
    "or",
    "please",
    "set",
    "shortcut",
    "symbol",
    "that",
    "the",
    "this",
    "to",
    "use",
    "with",
    "workflow",
}

ICON_QUERY_PATTERNS = [
    re.compile(
        r"\b(?:use|set|choose|pick|with|make)\s+(?:a|an|the)?\s*([a-z0-9][a-z0-9 '&+./_-]{1,60}?)\s+(?:icon|glyph|symbol)\b",
        re.I,
    ),
    re.compile(
        r"\b(?:icon|glyph|symbol)\s*(?:to|as|is|named|name)?\s*([a-z0-9][a-z0-9 '&+./_-]{1,60})\b",
        re.I,
    ),
    re.compile(r"\b(?:sf\s*symbol|sfsymbol|sf-symbol)\s*(?:to|as|is|named)?\s*([a-z0-9._+-]{1,60})\b", re.I),
]

GLYPH_NUMBER_PATTERNS = [
    re.compile(r"\b(?:glyph|icon|symbol)\s*(?:number|id|code)?\s*#?\s*(\d{5})\b", re.I),
    re.compile(r"\b#(\d{5})\b"),
]

HEX_COLOR_RE = re.compile(r"#([0-9a-fA-F]{6})\b")

COLOR_HINTS = {
    "Red": {"alert", "urgent", "danger", "critical", "alarm", "warning", "error", "security"},
    "Orange": {"warning", "caution", "attention"},
    "Yellow": {"sun", "bright", "sunny", "daylight"},
    "Gold": {"money", "finance", "budget", "expense", "invoice", "payment", "bank", "billing", "crypto"},
    "Green": {"health", "fitness", "run", "workout", "exercise", "wellness", "eco", "habit"},
    "Teal": {"automation", "shortcut", "workflow", "routine"},
    "Cyan": {"weather", "cloud", "sky", "water"},
    "Blue": {"travel", "map", "navigation", "flight", "internet", "network", "weather"},
    "Navy": {"business", "work", "professional", "productivity", "office"},
    "Purple": {"ai", "assistant", "creative", "music", "podcast", "magic", "design"},
    "Lavender": {"journal", "mindfulness", "dream", "calm"},
    "Pink": {"social", "chat", "message", "family", "love", "photo"},
    "Gray": {"system", "settings", "utility", "tools", "developer", "terminal", "debug"},
    "Sage": {"notes", "organize", "documents", "files", "archive"},
    "Tan": {"book", "read", "writing", "manual"},
}

ICON_HINTS: dict[int, set[str]] = {
    59714: {"weather", "forecast", "cloud", "sky"},
    59715: {"rain", "storm", "precipitation", "weather"},
    59395: {"expense", "expenses", "finance", "budget", "money", "invoice", "billing", "payment"},
    59680: {"calculator", "calculate", "sum", "totals", "math"},
    59412: {"translate", "translation", "language", "languages", "dictionary", "global", "international"},
    61529: {"terminal", "shell", "bash", "zsh", "cli", "developer", "code", "script", "command"},
    59414: {"message", "messages", "chat", "conversation", "text", "sms"},
    59773: {"mail", "email", "inbox", "envelope"},
    59682: {"camera", "photo", "picture", "snapshot", "image"},
    61459: {"photos", "gallery", "album", "images"},
    59790: {"music", "song", "audio", "playlist"},
    59816: {"podcast", "podcasts", "episodes"},
    59681: {"calendar", "date", "schedule", "event", "events"},
    61587: {"task", "tasks", "todo", "reminder", "checklist"},
    61444: {"map", "maps", "navigation", "route", "directions", "location"},
    59648: {"flight", "airplane", "travel", "airport"},
    59743: {"settings", "preferences", "config", "configuration"},
    59749: {"tools", "tool", "utility", "maintenance"},
    59870: {"fix", "repair", "debug", "troubleshoot"},
    61566: {"ai", "assistant", "chatgpt", "llm", "robot", "agent"},
    61581: {"magic", "sparkle", "generate", "rewrite", "enhance"},
    59711: {"clipboard", "copy", "paste", "snippet"},
    59819: {"qr", "qrcode", "scan", "scanner", "otp"},
    59661: {"barcode", "sku", "inventory"},
    59754: {"health", "heart", "wellness"},
    59808: {"run", "running", "fitness", "workout", "exercise"},
    59867: {"wifi", "network", "internet", "wireless"},
    59489: {"battery", "power", "charge"},
    59770: {"lock", "secure", "password", "security"},
    62501: {"shield", "protection", "defense", "security"},
    59725: {"document", "documents", "file", "files", "pdf"},
    59737: {"folder", "folders", "files"},
    61464: {"note", "notes", "memo"},
    59791: {"news", "article", "articles", "rss"},
}

LANGUAGE_HINT_TOKENS = {
    "translate",
    "translation",
    "language",
    "languages",
    "multilingual",
    "dictionary",
    "english",
    "spanish",
    "french",
    "german",
    "italian",
    "japanese",
    "chinese",
    "portuguese",
    "korean",
}


def _stem_token(token: str) -> str:
    if len(token) <= 3:
        return token
    if token.endswith("ies") and len(token) > 4:
        return token[:-3] + "y"
    if token.endswith("ing") and len(token) > 5:
        return token[:-3]
    if token.endswith("ed") and len(token) > 4:
        return token[:-2]
    if token.endswith("es") and len(token) > 4:
        if token[:-1].endswith("e"):
            return token[:-1]
        return token[:-2]
    if token.endswith("s") and len(token) > 4:
        return token[:-1]
    return token


def _normalize(text: str) -> str:
    text = text.strip()
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", text)
    text = text.lower()
    text = text.replace("_", " ").replace("-", " ")
    text = re.sub(r"[^a-z0-9#+ ]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _tokenize(text: str) -> list[str]:
    norm = _normalize(text)
    base_tokens = [t for t in norm.split() if t and t not in STOP_WORDS]
    tokens: list[str] = []
    seen: set[str] = set()
    for token in base_tokens:
        for candidate in (token, _stem_token(token)):
            if candidate and candidate not in STOP_WORDS and candidate not in seen:
                tokens.append(candidate)
                seen.add(candidate)
    return tokens


def _rgb_from_hex(hex_value: str) -> tuple[int, int, int]:
    value = hex_value.lstrip("#")
    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)


def _distance_rgb(a: tuple[int, int, int], b: tuple[int, int, int]) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _load_data(skill_root: Path) -> tuple[dict[str, str], dict[str, dict[str, Any]], list[dict[str, Any]]]:
    data_dir = skill_root / "data"
    glyph_map = _load_json(data_dir / "shortcuts-official-glyph-mapping.json")
    glyph_synonyms = _load_json(data_dir / "shortcuts-glyph-synonyms.json")
    colors = _load_json(data_dir / "shortcuts-icon-colors.json")
    return glyph_map, glyph_synonyms, colors


def _build_index(glyph_map: dict[str, str], glyph_synonyms: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    index: list[dict[str, Any]] = []

    for glyph_str, official_name in glyph_map.items():
        entry = glyph_synonyms.get(glyph_str, {})
        display_name = entry.get("name") or official_name
        synonyms = entry.get("synonyms") or []

        terms = [display_name, official_name, *synonyms]
        norm_terms: list[str] = []
        seen_terms: set[str] = set()
        for term in terms:
            if not isinstance(term, str):
                continue
            norm = _normalize(term)
            if norm and norm not in seen_terms:
                norm_terms.append(norm)
                seen_terms.add(norm)

        name_tokens = set(_tokenize(display_name)) | set(_tokenize(official_name))
        syn_tokens: set[str] = set()
        for syn in synonyms:
            if isinstance(syn, str):
                syn_tokens.update(_tokenize(syn))

        index.append(
            {
                "glyph": int(glyph_str),
                "name": display_name,
                "official_name": official_name,
                "norm_name": _normalize(display_name),
                "terms": norm_terms,
                "name_tokens": name_tokens,
                "syn_tokens": syn_tokens,
                "all_tokens": name_tokens | syn_tokens,
            }
        )

    return index


def _extract_explicit_glyph(prompt: str, glyph_map: dict[str, str]) -> tuple[int | None, str | None]:
    for pattern in GLYPH_NUMBER_PATTERNS:
        match = pattern.search(prompt)
        if not match:
            continue
        glyph = int(match.group(1))
        if str(glyph) in glyph_map:
            return glyph, f"explicit glyph number {glyph}"

    return None, None


def _extract_icon_query(prompt: str) -> str | None:
    for pattern in ICON_QUERY_PATTERNS:
        match = pattern.search(prompt)
        if not match:
            continue
        query = match.group(1).strip(" .,!?:;\"'()[]{}")
        if query:
            return query
    return None


def _score_icon(entry: dict[str, Any], query: str, explicit: bool) -> int:
    query_norm = _normalize(query)
    query_tokens = set(_tokenize(query))
    if not query_norm and not query_tokens:
        return 0

    score = 0
    boost = 1.35 if explicit else 1.0

    if query_norm:
        if query_norm == entry["norm_name"]:
            score += int(260 * boost)
        if query_norm in entry["terms"]:
            score += int(230 * boost)
        for term in entry["terms"]:
            if term.startswith(query_norm) and query_norm != term:
                score += int(150 * boost)
            elif query_norm in term and query_norm != term:
                score += int(100 * boost)

    overlap_name = len(query_tokens & entry["name_tokens"])
    overlap_syn = len(query_tokens & entry["syn_tokens"])
    score += int(overlap_name * 34 * boost)
    score += int(overlap_syn * 20 * boost)

    if query_tokens:
        overlap_all = len(query_tokens & entry["all_tokens"])
        if overlap_all == len(query_tokens):
            score += int(45 * boost)
        elif overlap_all >= 2:
            score += int(20 * boost)

    icon_hint_terms = ICON_HINTS.get(entry["glyph"], set())
    if icon_hint_terms and query_tokens:
        overlap_hint = len(query_tokens & icon_hint_terms)
        if overlap_hint:
            score += int(overlap_hint * 32 * boost)
            if overlap_hint >= 2:
                score += int(22 * boost)

    if entry["glyph"] in {59412, 62305} and query_tokens:
        lang_overlap = len(query_tokens & LANGUAGE_HINT_TOKENS)
        if lang_overlap:
            score += int(lang_overlap * 30 * boost)

    if explicit and query_tokens:
        missing = len(query_tokens - entry["all_tokens"])
        score -= missing * 6

    return score


def _resolve_icon(
    prompt: str,
    icon_override: str | None,
    glyph_map: dict[str, str],
    index: list[dict[str, Any]],
    top: int,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    explicit_glyph, explicit_glyph_reason = (None, None)
    if icon_override is None:
        explicit_glyph, explicit_glyph_reason = _extract_explicit_glyph(prompt, glyph_map)

    if explicit_glyph is not None:
        name = glyph_map[str(explicit_glyph)]
        icon = {
            "glyph_number": explicit_glyph,
            "symbol_name": name,
            "selection_mode": "explicit",
            "reason": explicit_glyph_reason,
            "confidence": 1.0,
        }
        candidates = [{"glyph_number": explicit_glyph, "symbol_name": name, "score": 999}]
        return icon, candidates

    explicit_query = _normalize(icon_override or "") if icon_override else None
    if not explicit_query:
        explicit_query = _extract_icon_query(prompt)

    query = explicit_query or prompt
    explicit = bool(explicit_query)

    scored = []
    for entry in index:
        score = _score_icon(entry, query, explicit)
        if score > 0:
            scored.append((score, entry))
    scored.sort(key=lambda item: item[0], reverse=True)

    if not scored:
        fallback_name = glyph_map.get(str(DEFAULT_GLYPH), "shortcuts")
        icon = {
            "glyph_number": DEFAULT_GLYPH,
            "symbol_name": fallback_name,
            "selection_mode": "fallback",
            "reason": "no relevant icon match in prompt",
            "confidence": 0.0,
        }
        return icon, [{"glyph_number": DEFAULT_GLYPH, "symbol_name": fallback_name, "score": 0}]

    top_score, best = scored[0]
    second_score = scored[1][0] if len(scored) > 1 else 0

    low_confidence = top_score < (120 if explicit else 20)
    tieish = second_score > 0 and top_score / max(second_score, 1) < 1.08

    if not explicit and low_confidence and tieish:
        fallback_name = glyph_map.get(str(DEFAULT_GLYPH), "shortcuts")
        icon = {
            "glyph_number": DEFAULT_GLYPH,
            "symbol_name": fallback_name,
            "selection_mode": "fallback",
            "reason": "prompt is too generic; defaulting to shortcuts icon",
            "confidence": 0.1,
        }
    else:
        mode = "explicit" if explicit else "inferred"
        reason_query = explicit_query or prompt
        confidence = min(0.99, max(0.2, top_score / 260.0))
        icon = {
            "glyph_number": best["glyph"],
            "symbol_name": best["name"],
            "selection_mode": mode,
            "reason": f"matched query '{reason_query}'",
            "confidence": round(confidence, 3),
        }

    candidates: list[dict[str, Any]] = []
    for score, entry in scored[: max(1, top)]:
        candidates.append(
            {
                "glyph_number": entry["glyph"],
                "symbol_name": entry["name"],
                "score": score,
            }
        )

    return icon, candidates


def _extract_color_query(prompt: str, colors: list[dict[str, Any]]) -> str | None:
    if match := HEX_COLOR_RE.search(prompt):
        return f"#{match.group(1)}"

    color_names = [c["name"].lower() for c in colors]
    name_pattern = "|".join(re.escape(name) for name in color_names)
    patterns = [
        re.compile(rf"\b(?:icon|shortcut)\s*(?:color|colour)\s*(?:to|as|is|=)?\s*({name_pattern})\b", re.I),
        re.compile(rf"\b({name_pattern})\b(?=[^.!?]{{0,24}}\b(?:icon|glyph|symbol|color|colour)\b)", re.I),
        re.compile(rf"\b(?:color|colour)\s+(?:it\s+)?({name_pattern})\b", re.I),
    ]
    for pattern in patterns:
        match = pattern.search(prompt)
        if match:
            return match.group(1)

    return None


def _resolve_color_by_alias(query: str, colors: list[dict[str, Any]]) -> tuple[dict[str, Any] | None, str | None]:
    normalized = _normalize(query)
    if not normalized:
        return None, None

    for color in colors:
        if normalized == _normalize(color["name"]):
            return color, f"explicit color name '{query}'"

    for color in colors:
        for synonym in color.get("synonyms", []):
            if normalized == _normalize(synonym):
                return color, f"explicit color synonym '{query}'"

    try:
        numeric = int(normalized)
    except ValueError:
        numeric = None

    if numeric is not None:
        for color in colors:
            if numeric == int(color["value"]) or numeric in [int(v) for v in color.get("aliases", [])]:
                return color, f"explicit color value {numeric}"

    return None, None


def _resolve_color(
    prompt: str,
    color_override: str | None,
    colors: list[dict[str, Any]],
    icon: dict[str, Any],
) -> dict[str, Any]:
    explicit_query = color_override or _extract_color_query(prompt, colors)

    if explicit_query:
        if explicit_query.startswith("#") and len(explicit_query) == 7:
            target_rgb = _rgb_from_hex(explicit_query)
            closest = min(colors, key=lambda color: _distance_rgb(target_rgb, _rgb_from_hex(color["hex"])))
            return {
                "value": int(closest["value"]),
                "name": closest["name"],
                "hex": closest["hex"],
                "selection_mode": "explicit",
                "reason": f"closest palette color to {explicit_query}",
            }

        color_match, reason = _resolve_color_by_alias(explicit_query, colors)
        if color_match:
            return {
                "value": int(color_match["value"]),
                "name": color_match["name"],
                "hex": color_match["hex"],
                "selection_mode": "explicit",
                "reason": reason,
            }

    prompt_tokens = set(_tokenize(prompt))
    icon_tokens = set(_tokenize(icon.get("symbol_name", "")))

    best_color = None
    best_score = 0
    for color in colors:
        score = 0
        color_name = color["name"]

        score += len(prompt_tokens & { _normalize(color_name) }) * 20

        for synonym in color.get("synonyms", []):
            syn_token_set = set(_tokenize(synonym))
            if syn_token_set:
                overlap = len(prompt_tokens & syn_token_set)
                score += overlap * 6

        for hint in COLOR_HINTS.get(color_name, set()):
            hint_tokens = set(_tokenize(hint))
            if hint_tokens and hint_tokens <= prompt_tokens:
                score += 14
            elif hint_tokens and prompt_tokens & hint_tokens:
                score += 6

        # A small bias to keep icon + color visually coherent for known themes.
        if color_name == "Purple" and {"robot", "brain", "sparkles"} & icon_tokens:
            score += 8
        if color_name == "Gold" and {"dollar", "dollar sign", "credit card"} & icon_tokens:
            score += 8
        if color_name == "Blue" and {"cloud", "airplane", "map"} & icon_tokens:
            score += 8
        if color_name == "Gray" and {"gear", "tools", "wrench", "command"} & icon_tokens:
            score += 8

        if score > best_score:
            best_score = score
            best_color = color

    if best_color is None or best_score == 0:
        default = next((c for c in colors if int(c["value"]) == DEFAULT_COLOR_VALUE), colors[0])
        return {
            "value": int(default["value"]),
            "name": default["name"],
            "hex": default["hex"],
            "selection_mode": "fallback",
            "reason": "no explicit or thematic color match; using default",
        }

    return {
        "value": int(best_color["value"]),
        "name": best_color["name"],
        "hex": best_color["hex"],
        "selection_mode": "inferred",
        "reason": "matched prompt theme keywords",
    }


def resolve_icon_color(prompt: str, icon_override: str | None, color_override: str | None, top: int = 5) -> dict[str, Any]:
    script_path = Path(__file__).resolve()
    skill_root = script_path.parents[1]

    glyph_map, glyph_synonyms, colors = _load_data(skill_root)
    index = _build_index(glyph_map, glyph_synonyms)

    icon, icon_candidates = _resolve_icon(prompt, icon_override, glyph_map, index, top)
    color = _resolve_color(prompt, color_override, colors, icon)

    return {
        "prompt": prompt,
        "icon": icon,
        "color": color,
        "wf_workflow_icon": {
            "WFWorkflowIconGlyphNumber": int(icon["glyph_number"]),
            "WFWorkflowIconStartColor": int(color["value"]),
        },
        "icon_candidates": icon_candidates,
        "color_palette": [
            {
                "name": c["name"],
                "hex": c["hex"],
                "value": int(c["value"]),
            }
            for c in colors
        ],
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Resolve Shortcuts icon/color from natural language")
    parser.add_argument("--prompt", required=True, help="Original user prompt used to build the shortcut")
    parser.add_argument("--icon", default=None, help="Optional explicit icon query (name/synonym/glyph number)")
    parser.add_argument("--color", default=None, help="Optional explicit color query (name/synonym/value/#RRGGBB)")
    parser.add_argument("--top", type=int, default=5, help="How many icon candidates to include")
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    payload = resolve_icon_color(args.prompt, args.icon, args.color, top=max(1, args.top))
    print(json.dumps(payload, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
