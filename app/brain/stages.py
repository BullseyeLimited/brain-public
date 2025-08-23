from __future__ import annotations
from typing import Dict, Tuple, List

# Stages are coarse "missions"
STAGE_IDS = [
    "discovery_basic",
    "rapport_value_add",
    "soft_tease",
    "ppv_pitch",
    "aftercare_checkin",
    "cooling_off",
]

def score_stages(signals: Dict[str, float | int | bool]) -> Dict[str, float]:
    s = {k: float(v) if isinstance(v,(int,float)) else (1.0 if v else 0.0) for k,v in signals.items()}

    base: Dict[str, float] = {k: 0.5 for k in STAGE_IDS}

    # Increase rapport/discovery when sentiment good or question asked
    base["discovery_basic"]   += 0.4 * max(0.0, s.get("question_ratio", 0.0))
    base["rapport_value_add"] += 0.3 * max(0.0, s.get("sentiment_score", 0.0))

    # Soft tease when escalation interest OR good sentiment
    base["soft_tease"] += 0.3 * max(s.get("escalation",0.0), 0.0) + 0.2*max(0.0, s.get("sentiment_score",0.0))

    # PPV pitch when price intent or high escalation
    base["ppv_pitch"] += 0.6*max(0.0, s.get("price_intent",0.0)) + 0.5*max(0.0, s.get("escalation",0.0))

    # Aftercare when price intent low and sentiment is non-negative
    base["aftercare_checkin"] += 0.1 + 0.1*max(0.0, s.get("sentiment_score",0.0))

    # Cooling off is low by default, encourage when sentiment negative
    base["cooling_off"] += 0.6*max(0.0, -s.get("sentiment_score", 0.0))

    # Normalize to 0..1
    mx = max(base.values()) or 1.0
    for k in base:
        base[k] = round(base[k]/mx, 3)
    return base
