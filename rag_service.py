"""Small deterministic keyword retrieval; no vector DB, no web requests."""
import json
import re
from pathlib import Path

RULES = json.loads((Path(__file__).resolve().parent / "language_rules.json").read_text(encoding="utf-8"))

def retrieve_rules(text: str, limit: int = 4) -> list[dict]:
    words = set(re.findall(r"[\wəğıöüşçƏĞIİÖÜŞÇ]+", text.casefold()))
    text_lower = text.casefold()
    scored = []
    for rule in RULES:
        score = sum(2 if k.casefold() in words else 1 if k.casefold() in text_lower else 0 for k in rule["keywords"])
        if score:
            scored.append((score, rule))
    scored.sort(key=lambda pair: -pair[0])
    return [rule for _, rule in scored[:limit]]

def build_context(text: str) -> tuple[str, list[dict]]:
    selected = retrieve_rules(text)
    lines = []
    for rule in selected:
        lines.append(f"[{rule['id']}] {rule['title']}: {rule['guidance']}")
    return "\n".join(lines) or "No relevant rule was retrieved.", selected
