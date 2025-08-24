# brain/signalizer.py
"""
Signalizer placeholder.
In production, compute reply_urgency, curiosity, boundary tone, etc.
"""
from typing import Dict, Any

def compute_signals(last_messages: list) -> Dict[str, Any]:
    # Dummy output for demo; replace with real computation
    return {
        "reply_urgency": "medium",
        "price_readiness": 0.2,
        "curiosity_cue": True,
        "interruption": False,
        "cooldown_pressure": "low",
        "novelty_budget": 0.6,
        "boundary_tone": "none"
    }
