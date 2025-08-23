from __future__ import annotations
from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field

# ---- Message DTOs ----
class MessageLine(BaseModel):
    text: str

class Messages(BaseModel):
    fan_last: List[MessageLine] = Field(default_factory=list)
    creator_last: List[MessageLine] = Field(default_factory=list)

class Memory(BaseModel):
    storybook: Optional[str] = ""
    facts: List[str] = Field(default_factory=list)

class Profile(BaseModel):
    fan_id: Optional[str] = None
    tier: Literal["silver","gold","diamond","emerald"] = "silver"
    relationship_age_days: int = 0

class Budgets(BaseModel):
    max_paid_per_24h_user: float = 5.0
    min_hours_between_paid: float = 0.75
    price_floor: float = 9.0
    price_ceiling: float = 120.0
    price_step: float = 1.0
    exploration_quota: float = 0.2
    compute_tier: Literal["cheap","balanced","premium"] = "balanced"

class Context(BaseModel):
    local_hour: int = 12
    consecutive_no_reply: int = 0
    tz: Optional[str] = None

class Signals(BaseModel):
    reply_urgency: float = 0.5     # 0..1
    sentiment_score: float = 0.0   # -1..1
    price_intent: float = 0.0      # 0..1
    fan_burst_count: int = 1
    interruption: bool = False
    question_density: float = 0.0
    imperative_hits: int = 0
    style_fp: Dict[str, float] = Field(default_factory=dict)

class CatalogItem(BaseModel):
    ppv_asset_id: str
    media_type: Literal["photo","video","bundle"]
    tags: List[str] = Field(default_factory=list)
    base_price: float
    description: str

# ---- Pack for the chatter ----
class Bubble(BaseModel):
    text: str

class Pack(BaseModel):
    send_mode: Literal["single","burst"] = "single"
    bubbles: List[Bubble]

# ---- Writer instructions ----
class WriterDeliveryStyle(BaseModel):
    bubble_count: int = 1
    send_mode: Literal["single","burst"] = "single"
    max_chars: int = 220
    paragraph: Literal["none","micro","long"] = "none"
    emoji_only: bool = False
    reaction_hint: Optional[str] = None
    pacing_flavor: Literal["neutral","snappy","hesitant","cozy"] = "neutral"
    emoji_level: int = 2

class Mirroring(BaseModel):
    use_emoji: bool = True
    exclaimation_tolerance: Literal["low","med","high"] = "low"
    question_echo: bool = False
    lexical_tone_hint: Optional[str] = None

class WriterStyle(BaseModel):
    max_chars: int = 220
    no_price: bool = True
    one_question_max: bool = True

class WriterInstructions(BaseModel):
    tone: Literal["playful","warm","direct","cozy","sultry"] = "playful"
    angle: str = "light tease"
    talk_about: List[str] = Field(default_factory=list)
    petnames: List[str] = Field(default_factory=list)
    delivery_style: WriterDeliveryStyle = Field(default_factory=WriterDeliveryStyle)
    mirroring: Mirroring = Field(default_factory=Mirroring)
    style: WriterStyle = Field(default_factory=WriterStyle)

class PPVPlan(BaseModel):
    ppv_asset_id: str
    price: float
    description: str

class Decision(BaseModel):
    mission: str
    chosen_id: str
    pack: Pack
    writer_instructions: WriterInstructions
    ppv: Optional[PPVPlan] = None
    why: List[Dict[str, Any]] = Field(default_factory=list)
    alternatives: List[Dict[str, Any]] = Field(default_factory=list)
    budget_used: Dict[str, Any] = Field(default_factory=dict)
    send_now: bool = True
    send_at: Optional[str] = None

class BrainInput(BaseModel):
    messages: Messages
    memory: Memory = Field(default_factory=Memory)
    signals: Signals = Field(default_factory=Signals)
    profile: Profile = Field(default_factory=Profile)
    budgets: Budgets = Field(default_factory=Budgets)
    context: Context = Field(default_factory=Context)
    catalog: Optional[List[CatalogItem]] = None
