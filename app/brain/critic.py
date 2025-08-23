from __future__ import annotations
from typing import List
from .contracts import BrainInput

def _family_of(cid: str) -> str:
    # e.g., "soft_tease_v1" -> "soft_tease"
    if "_v" in cid:
        return cid.split("_v", 1)[0]
    parts = cid.split("_")
    return "_".join(parts[:-1]) if len(parts) > 1 else cid

def choose(inp: BrainInput, brief, cands: List) -> any:
    if not cands:
        raise ValueError("no candidates")
    best = None
    best_score = -1.0
    for c in cands:
        score = float(getattr(c, "forecast", 0.5))
        fam = _family_of(c.id)
        if fam != brief.mission:
            score *= 0.97  # gentle penalty for mission-family mismatch
        # small boost if interruption and candidate packs >1 bubble (feel live)
        try:
            if inp.signals.interruption and len(c.pack.bubbles) >= 2:
                score *= 1.02
        except Exception:
            pass
        if score > best_score:
            best, best_score = c, score
    return best
