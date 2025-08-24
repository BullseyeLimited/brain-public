# brain/strategist/python/service.py
from __future__ import annotations
import json
from pathlib import Path
from pydantic import ValidationError
from .contracts import StrategistInput, StrategistOut

class StrategistService:
    """Build user prompt, call LLM, validate StrategistOut."""
    def __init__(self, root: str):
        # Anchor prompts/contracts to THIS package (no external path guessing)
        pkg_root = Path(__file__).resolve().parents[1]  # brain/strategist
        prom_dir = pkg_root / "prompts"
        if not prom_dir.exists():
            raise RuntimeError(f"Missing prompts at {prom_dir}. Create files below:\n"
                               f"- {prom_dir/'strategist.system.txt'}\n"
                               f"- {prom_dir/'strategist.user_template.txt'}")
        self.system_prompt = (prom_dir / "strategist.system.txt").read_text(encoding="utf-8")
        self.user_template = (prom_dir / "strategist.user_template.txt").read_text(encoding="utf-8")

        contracts_dir = pkg_root / "contracts"
        self.in_schema = json.loads((contracts_dir / "strategist_in.schema.json").read_text(encoding="utf-8"))
        self.out_schema = json.loads((contracts_dir / "strategist_out.schema.json").read_text(encoding="utf-8"))

    def build_user_prompt(self, s_in: StrategistInput) -> str:
        payload = {
            "thread_id": s_in.thread_id,
            "turn": s_in.turn,
            "scene_card": s_in.scene_card.model_dump(),
            "persona_pack": s_in.persona_pack.model_dump(),
            "signals": s_in.signals.model_dump(),
            "goal_vector": s_in.goal_vector,
            "compass_shadows": [sh.model_dump() for sh in s_in.compass_shadows],
            "variety_window_signatures": s_in.variety_window_signatures,
            "policy": s_in.policy.model_dump(),
            "priors": s_in.priors.model_dump(),
        }
        return self.user_template.replace("{{INPUT_JSON}}", json.dumps(payload, ensure_ascii=False))

    def plan(self, s_in: StrategistInput, llm_call) -> StrategistOut:
        user_prompt = self.build_user_prompt(s_in)
        raw = llm_call(self.system_prompt, user_prompt)
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Strategist JSON parse error: {e}\nRaw: {raw[:400]}")
        try:
            out = StrategistOut.model_validate(data)
        except ValidationError as ve:
            raise RuntimeError(f"Strategist schema validation failed: {ve}")
        return out
