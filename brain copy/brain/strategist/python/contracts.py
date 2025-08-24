# brain/strategist/python/contracts.py
from __future__ import annotations
from typing import List, Dict, Optional, Literal
from pydantic import BaseModel, Field

class StyleFingerprint(BaseModel):
    avg_chars: float
    question_rate: float
    emoji_tolerance: Literal["low", "medium", "high"]
    burstiness: Literal["low", "medium", "high"]

class Rails(BaseModel):
    turns_since_offer: int
    offers_last_10: int
    turns_since_rejection: int

class SceneCard(BaseModel):
    topics_snapshot: List[str]
    warmth: float
    curiosity: float
    sentiment_delta: float
    tier: str
    relationship_stage: Optional[Literal["Silver","Gold","Diamond","Emerald"]] = None
    intimacy_index: Optional[float] = None
    trust_index: Optional[float] = None
    aftercare_need: Optional[float] = None
    sexting_consent_state: Optional[Literal["none","invited","ongoing","paused"]] = None
    roleplay_tolerance: Optional[float] = None
    style_fingerprint: StyleFingerprint
    rails: Rails

class PersonaPack(BaseModel):
    tone_sliders: Dict[str, float]
    petnames: List[str]
    emoji_budget: Dict[str, int]
    jealousy_tolerance: Literal["low","medium","high"]

class Signals(BaseModel):
    reply_urgency: Literal["low","medium","high"]
    price_readiness: float
    curiosity_cue: bool
    interruption: bool
    cooldown_pressure: Literal["low","medium","high"]
    novelty_budget: float
    boundary_tone: Literal["none","soft","hard"]

class Shadow(BaseModel):
    shadow_id: str
    tags: List[str]
    safety_grade: Literal["SFW","suggestive"]

class Policy(BaseModel):
    allowed_missions: List[str]
    allowed_levers: List[str]
    gating_flags: Dict[str, bool]   # no_explicit, writer_blind_to_price, respect_boundaries
    tier_budgets: Dict[str, float]  # vulnerability, jealousy, intimacy

class Priors(BaseModel):
    mission_prior: Dict[str, float]
    maneuver_prior: Dict[str, float]
    delivery_prior: Dict[str, float]
    exploration: float

class StrategistInput(BaseModel):
    thread_id: str
    turn: int
    scene_card: SceneCard
    persona_pack: PersonaPack
    signals: Signals
    goal_vector: Dict[str, float]
    compass_shadows: List[Shadow]
    variety_window_signatures: List[str]
    policy: Policy
    priors: Priors

class Delivery(BaseModel):
    bubbles: int = Field(ge=1, le=3)
    para: Literal["short","med","long"]
    mirroring: Literal["low","med","high"]
    emoji_budget: int = Field(ge=0, le=2)
    cadence: Literal["burst","steady"]
    ask_rate: Literal["low","med","high"]

class ConvoLever(BaseModel):
    type: Literal["harvest","seed","invite","callback_memory","boundary_affirm",
                  "humor","repair","aftercare_hook","consent_check","jealousy_soft"]
    text: str
    goal_token: Literal["reply_token","data_token","curiosity_token","consent_soft",
                        "respect_token","opt_in_signal","novelty_token","promise_kept"]
    shadow_id: Optional[str] = None

class SafetyConstraints(BaseModel):
    no_explicit: bool = True
    respect_boundaries: bool = True
    jealousy_cap: float
    vulnerability_cap: float
    intimacy_cap: float

class StrategistOut(BaseModel):
    plan_version: str = "2025-08-23.v2"
    mission: Literal["onboarding_first_impression","discovery_surface","discovery_personal",
                     "bond","playful_flirt","tease_soft","tension_build","consent_seed",
                     "sexting_suggestive","sexting_aftercare","roleplay_light",
                     "vulnerability_share","long_form_deepen","jealousy_soft",
                     "aftercare","repair","reengage","prime_for_offer","post_offer_value"]
    angle: str
    talk_about: List[str]
    theme_tags: List[str]
    delivery: Delivery
    convo_levers: List[ConvoLever]
    micro_script: Optional[Dict[str, List[str]]] = None
    sell_intent: bool
    shadow_hints: List[str]
    safety_constraints: SafetyConstraints
    novelty_signature: str
    guaranteed_tokens: List[str]
    invariants: Dict[str, bool]
    why: Optional[str] = None
