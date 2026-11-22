"""Unicode-aware Levenshtein alignment and OCR metrics."""
import re
from difflib import SequenceMatcher


def alignment(prediction: str, reference: str) -> dict:
    a, b = list(prediction), list(reference)
    m, n = len(a), len(b)
    # Limit memory/time on accidentally huge pasted texts.
    if m > 12000 or n > 12000 or m * n > 2_000_000:
        raise ValueError("Mətn müqayisə üçün çox uzundur (maksimum 2 milyon hüceyrə).")
    prev = list(range(n + 1))
    directions = [bytearray(n + 1) for _ in range(m + 1)]
    for j in range(1, n + 1):
        directions[0][j] = 2  # insert missing reference character
    for i in range(1, m + 1):
        directions[i][0] = 3  # delete extra prediction character
        row = [i] + [0] * n
        for j in range(1, n + 1):
            sub = prev[j-1] + (a[i-1] != b[j-1])
            delete = prev[j] + 1
            insert = row[j-1] + 1
            best = min(sub, delete, insert)
            row[j] = best
            directions[i][j] = 0 if best == sub and a[i-1] == b[j-1] else (1 if best == sub else (3 if best == delete else 2))
        prev = row
    i, j = m, n
    ops = []
    counts = {"substitutions": 0, "insertions": 0, "deletions": 0}
    while i or j:
        op = directions[i][j]
        if op == 0:
            i -= 1; j -= 1
            ops.append({"operation": "equal", "original": a[i], "expected": b[j]})
        elif op == 1:
            i -= 1; j -= 1
            counts["substitutions"] += 1
            ops.append({"operation": "substitute", "original": a[i], "expected": b[j]})
        elif op == 2:
            j -= 1
            counts["insertions"] += 1
            ops.append({"operation": "insert", "original": "", "expected": b[j]})
        else:
            i -= 1
            counts["deletions"] += 1
            ops.append({"operation": "delete", "original": a[i], "expected": ""})
    ops.reverse()
    return {"operations": ops, "distance": prev[n], "counts": counts,
            "cer_percent": round(100 * prev[n] / n, 2) if n else (0.0 if not m else None)}


def word_error_rate(prediction: str, reference: str):
    a = prediction.split()
    b = reference.split()
    if not b:
        return 0.0 if not a else None
    prev = list(range(len(b)+1))
    for i, word in enumerate(a, 1):
        row = [i]
        for j, ref in enumerate(b, 1):
            row.append(min(prev[j]+1, row[-1]+1, prev[j-1]+(word != ref)))
        prev = row
    return round(100 * prev[-1] / len(b), 2)
