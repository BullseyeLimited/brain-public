from __future__ import annotations
from typing import Any, Dict
from .contracts import BrainInput

class Brief:
    def __init__(self, mission: str, why: Dict[str, Any]):
        self.mission = mission
        self.why = why

def pick_mission(inp: BrainInput) -> Brief:
    s = inp.signals
    # Default mission
    mission = "rapport_value_add"
    reason = {"reason": "baseline rapport", "signals": s.model_dump()}

    if s.price_intent >= 0.5:
        mission = "ppv_pitch"
        reason = {"reason": "high price intent", "signals": s.model_dump()}
    elif s.interruption and s.reply_urgency >= 0.55:
        # fan is actively pinging; keep it light/teasy to maintain flow
        mission = "soft_tease"
        reason = {"reason": "fan burst + pinging", "signals": s.model_dump()}
    elif s.question_density >= 0.5:
        mission = "discovery_basic"
        reason = {"reason": "lots of questions", "signals": s.model_dump()}
    elif s.sentiment_score <= -0.3:
        mission = "aftercare_checkin"
        reason = {"reason": "cool/negative vibe", "signals": s.model_dump()}

    return Brief(mission, reason)
