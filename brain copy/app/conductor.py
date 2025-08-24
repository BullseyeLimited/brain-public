# brain/conductor.py
"""
Orchestrator placeholder.
Build StrategistInput from your Archivist/Signalizer output and call StrategistService.
"""

import json
from pathlib import Path
from typing import Callable

from brain.strategist.python import StrategistService, StrategistInput, StrategistOut

def plan_turn(bundle: dict, llm_call: Callable[[str, str], str]) -> StrategistOut:
    svc = StrategistService(root=str(Path(__file__).resolve().parents[1]))
    s_in = StrategistInput.model_validate(bundle)
    return svc.plan(s_in, llm_call)
