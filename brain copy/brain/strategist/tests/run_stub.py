import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(".").resolve()))

from brain.strategist.python import StrategistService, StrategistInput  # type: ignore

def llm_stub(system_prompt: str, user_prompt: str) -> str:
    plan = {
      "plan_version":"2025-08-23.v2",
      "mission":"bond",
      "angle":"quick warm catch-up anchored to the last topic",
      "talk_about":["weekend plan","memory callback"],
      "theme_tags":["warm","memory"],
      "delivery":{"bubbles":2,"para":"short","mirroring":"med","emoji_budget":1,"cadence":"steady","ask_rate":"low"},
      "convo_levers":[
        {"type":"callback_memory","text":"call back a small detail from earlier","goal_token":"reply_token"}
      ],
      "micro_script":{"on_direct_answer":["mirror + tiny curiosity ask"]},
      "sell_intent":False,
      "shadow_hints":[],
      "safety_constraints":{"no_explicit":True,"respect_boundaries":True,"jealousy_cap":0.2,"vulnerability_cap":0.3,"intimacy_cap":0.3},
      "novelty_signature":"bond:catchup:memory",
      "guaranteed_tokens":["reply_token"],
      "invariants":{"writer_blind_to_price":True,"no_time_promises":True},
      "why":"stub ok"
    }
    return json.dumps(plan, ensure_ascii=False)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".", help="project root (unused)")
    ap.add_argument("--input", required=True, help="StrategistInput JSON path")
    args = ap.parse_args()

    bundle = json.loads(Path(args.input).read_text(encoding="utf-8"))
    svc = StrategistService(root=".")
    s_in = StrategistInput.model_validate(bundle)
    out = svc.plan(s_in, llm_stub)
    print(json.dumps(out.model_dump(), indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
