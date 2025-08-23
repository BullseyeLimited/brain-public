# filepath: app/main.py
from __future__ import annotations

from typing import Optional, List, Dict, Any
from fastapi import FastAPI
from pydantic import BaseModel

# ---- Brain contracts & modules ----
from app.brain.contracts import (
    BrainInput, Decision, PPVPlan,
    Messages, Memory, Signals, Profile, Budgets, Context, CatalogItem,
    Pack, Bubble
)
from app.brain.conductor import pick_mission
from app.brain.strategist import plan_candidates
from app.brain.critic import choose
from app.brain.signalizer import derive_signals as basic_signals

app = FastAPI(title="brain", version="1.2.0")


# ---------------------------- health ----------------------------
@app.get("/healthz")
def healthz():
    return {"ok": True, "service": "brain", "version": "1.2.0"}


# ---------------------- helpers / demo catalog -------------------
def _ensure_catalog(catalog: Optional[List[CatalogItem]]) -> List[CatalogItem]:
    """
    If caller doesn't pass a catalog, we return a small PG demo set so you can test end-to-end.
    """
    if catalog is not None and len(catalog) > 0:
        return catalog
    return [
        CatalogItem(
            ppv_asset_id="ppv_1001",
            title="Mirror tease set",
            description="Playful mirror set in black lace—smiles & curves.",
            media_type="photo",
            tags=["tease", "lingerie", "mirror"],
            base_price=10.0,
        ),
        CatalogItem(
            ppv_asset_id="ppv_2001",
            title="Flirty bedroom mini",
            description="Short playful clip, cozy vibe, sweet & suggestive.",
            media_type="video",
            tags=["tease", "cozy"],
            base_price=18.0,
        ),
        CatalogItem(
            ppv_asset_id="ppv_3001",
            title="Cute voice note",
            description="Soft voice note saying hi and asking about your day.",
            media_type="voice",
            tags=["voice", "soft"],
            base_price=12.0,
        ),
        CatalogItem(
            ppv_asset_id="ppv_9001",
            title="Bundle: weekend set",
            description="Mixed bundle of tasteful photos & a short playful clip.",
            media_type="bundle",
            tags=["bundle", "weekend"],
            base_price=25.0,
        ),
    ]


# ------------------------ /decide (signals-in) -------------------
@app.post("/decide", response_model=Decision)
def decide(inp: BrainInput):
    """
    You provide Signals inside BrainInput. Planner → Strategist → Critic.
    Returns a Decision with:
      - pack (burst, no wait)
      - writer_instructions (WHAT to write for persona; dict)
      - optional ppv
    """
    # Plan mission (returns {"mission": ..., "why": {...}})
    brief = pick_mission(inp)

    # Build candidates (now include delivery/mirroring in writer_instructions dict)
    cands = plan_candidates(inp, brief)

    # Choose best (signature: choose(inp, brief, cands))
    chosen = choose(inp, brief, cands)

    # Optional PPV plan for ppv_pitch (tier-scaled & clamped)
    ppv: Optional[PPVPlan] = None
    if inp.catalog and inp.signals.price_intent >= 0.45 and brief["mission"] == "ppv_pitch":
        item = _ensure_catalog(inp.catalog)[0]
        tier_mult = {"silver": 1.0, "gold": 1.3, "diamond": 2.0, "emerald": 3.0}.get(inp.profile.tier, 1.0)
        price = item.base_price * tier_mult
        price = max(inp.budgets.price_floor,
                    min(inp.budgets.price_ceiling,
                        round(price / inp.budgets.price_step) * inp.budgets.price_step))
        ppv = PPVPlan(ppv_asset_id=item.ppv_asset_id, price=float(price), description=item.description)

    return Decision(
        mission=brief["mission"],
        chosen_id=chosen.id,
        pack=chosen.pack,                                  # bubbles only; NO waits
        ppv=ppv,
        writer_instructions=chosen.writer_instructions,    # dict: delivery_style + mirroring + angle/tone/talk_about
        why=[brief["why"]],
        alternatives=[{"id": c.id, "forecast": c.forecast} for c in cands if c.id != chosen.id],
        budget_used=inp.budgets.model_dump(),
        send_now=True,
        send_at=None,
    )


# --------------- /auto_decide (signals derived here) ---------------
class AutoIn(BaseModel):
    messages: Messages
    memory:  Memory  = Memory()
    profile: Profile = Profile()
    budgets: Budgets = Budgets()
    context: Context = Context()
    catalog: Optional[List[CatalogItem]] = None

@app.post("/auto_decide", response_model=Decision)
def auto_decide(inp: AutoIn):
    """
    Convenience: send raw messages; brain derives content-based signals
    (robust to operator paste-bursts), then runs the same pipeline.
    """
    # derive signals from the last fan lines
    sigs_dict = basic_signals(inp.messages)  # accepts Messages model
    # build BrainInput and reuse /decide
    core = BrainInput(
        messages=inp.messages,
        memory=inp.memory,
        signals=Signals(**sigs_dict),
        profile=inp.profile,
        budgets=inp.budgets,
        context=inp.context,
        catalog=_ensure_catalog(inp.catalog),
    )
    return decide(core)


# ----------------------- demo payload helper ----------------------
@app.get("/demo/auto_payload")
def demo_payload():
    return {
        "messages": {
            "fan_last":    [ {"role": "fan", "text": "hey babe 😊 what do you like? any pics"} ],
            "creator_last": []
        },
        "memory":  { "storybook": "we joked about tacos yesterday" },
        "profile": { "fan_id": "u1", "tier": "silver", "relationship_age_days": 3 },
        "budgets": {
            "max_paid_per_24h_user": 5,
            "min_hours_between_paid": 0.75,
            "price_floor": 9,
            "price_ceiling": 120,
            "price_step": 1.0,
            "exploration_quota": 0.2,
            "compute_tier": "balanced"
        },
        "context": {
            "local_hour": 21,
            "consecutive_no_reply": 0,
            "thread_timezone": "America/New_York"
        },
        "catalog": []
    }


# ----------------------- /suggest (compat shim) -------------------
@app.post("/suggest")
def suggest_compat(payload: Dict[str, Any], view: Optional[str] = None):
    """
    Accepts the legacy sidecar SuggestRequest shape:
      {
        "messages":[{"role":"fan"|"creator","text":"..."}],
        "profile": {...},
        "ppv_catalog": [...],
        "budget": {...},
        "settings": {...}
      }
    It converts to the brain's AutoIn, runs the same planner,
    and returns a SuggestResponse-like dict (so old tests pass).
    """

    # 1) Split recent messages into fan_last / creator_last (keep only text)
    msgs = payload.get("messages") or []
    fan_last     = [{"role":"fan","text": m.get("text","")} for m in msgs if m.get("role") == "fan"][-8:]
    creator_last = [{"role":"creator","text": m.get("text","")} for m in msgs if m.get("role") == "creator"][-8:]

    # 2) Profile & budgets
    prof = payload.get("profile") or {}
    tier = (prof.get("tier") or "silver").lower()
    if tier not in {"silver", "gold", "diamond", "emerald"}:
        tier = "silver"

    bud   = payload.get("budget") or {}
    budgets = Budgets(
        max_paid_per_24h_user = float(bud.get("max_paid_per_24h_user", 3)),
        min_hours_between_paid= float(bud.get("min_hours_between_paid", 1.0)),
        price_floor           = float(bud.get("price_floor", 9.0)),
        price_ceiling         = float(bud.get("price_ceiling", 120.0)),
        price_step            = float(bud.get("price_step", 1.0)),
        exploration_quota     = float(bud.get("exploration_quota", 0.2)),
        compute_tier          = bud.get("compute_tier", "balanced"),
    )

    # 3) Catalog (optional)
    cat_raw = payload.get("ppv_catalog") or []
    catalog = [
        CatalogItem(
            ppv_asset_id=c.get("ppv_asset_id","ppv_demo"),
            title=c.get("title") or c.get("name",""),
            description=c.get("description",""),
            media_type=(c.get("media_type") or "photo"),
            tags=c.get("tags",[]),
            base_price=float(c.get("base_price", budgets.price_floor)),
        )
        for c in cat_raw
    ] or None

    # 4) Build AutoIn and reuse the same pipeline
    auto = AutoIn(
        messages=Messages(
            fan_last=fan_last,
            creator_last=creator_last,
        ),
        memory=Memory(),
        profile=Profile(
            fan_id=str(prof.get("user_id") or prof.get("fan_id") or "u"),
            tier=tier,
            relationship_age_days=int(prof.get("relationship_age_days") or 0),
        ),
        budgets=budgets,
        context=Context(),
        catalog=catalog,
    )
    decision = auto_decide(auto)

    # 5) Return a legacy-like SuggestResponse (no waits; bubbles only)
    return {
        "chosen_stage_id": decision.mission,
        "chosen_strategy_id": decision.chosen_id,
        "send_now": decision.send_now,
        "send_at": decision.send_at,
        "message_pack": {
            "send_mode": decision.pack.send_mode,
            "bubbles": [{"text": b.text} for b in decision.pack.bubbles],
        },
        "ppv": (decision.ppv.dict() if decision.ppv else None),
        "why": decision.why,
        "alternatives": decision.alternatives,
        "budget_used": (decision.budget_used or {}),
    }