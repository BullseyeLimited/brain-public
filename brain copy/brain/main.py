# brain/main.py
import json
from pathlib import Path
from brain.strategist.python import StrategistService, StrategistInput

def main():
    sample = Path(__file__).resolve().parents[1] / "brain" / "strategist" / "tests" / "sample_bundle.json"
    bundle = json.loads(sample.read_text(encoding="utf-8"))
    svc = StrategistService(root=".")
    s_in = StrategistInput.model_validate(bundle)
    out = svc.plan(s_in, lambda sys,user: json.dumps({
        "plan_version":"2025-08-23.v2",
        "mission":"bond",
        "angle":"quick warm catch-up anchored to the last topic",
        "talk_about":["weekend plan","memory callback"],
        "theme_tags":["warm","memory"],
        "delivery":{"bubbles":2,"para":"short","mirroring":"med","emoji_budget":1,"cadence":"steady","ask_rate":"low"},
        "convo_levers":[{"type":"callback_memory","text":"call back a small detail from earlier","goal_token":"reply_token"}],
        "sell_intent": False,
        "shadow_hints": [],
        "safety_constraints":{"no_explicit":True,"respect_boundaries":True,"jealousy_cap":0.2,"vulnerability_cap":0.3,"intimacy_cap":0.3},
        "novelty_signature":"bond:catchup:memory",
        "guaranteed_tokens":["reply_token"],
        "invariants":{"writer_blind_to_price":True,"no_time_promises":True}
    }))
    print(json.dumps(out.model_dump(), indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
