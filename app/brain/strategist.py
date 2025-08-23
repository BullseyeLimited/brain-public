from __future__ import annotations
import re
from typing import List, Dict, Any
from .contracts import BrainInput, WriterInstructions, WriterDeliveryStyle, Mirroring, WriterStyle, Pack

class Candidate:
    def __init__(self, id: str, pack: Pack, forecast: float, wi: WriterInstructions):
        self.id = id
        self.pack = pack
        self.forecast = forecast
        self.wi = wi

# --- helpers ---
def _tier_emoji_cap(tier: str) -> int:
    return {"silver": 2, "gold": 3, "diamond": 3, "emerald": 3}.get(tier, 2)

def _build_delivery_style(inp: BrainInput) -> WriterDeliveryStyle:
    s = inp.signals
    ds = WriterDeliveryStyle()
    # Map urgency to delivery
    if s.reply_urgency < 0.35:
        ds.bubble_count = 1
        ds.send_mode = "single"
        ds.paragraph = "micro"
        ds.pacing_flavor = "cozy"
    elif s.reply_urgency > 0.7 or s.fan_burst_count >= 2:
        ds.bubble_count = 2
        ds.send_mode = "burst"
        ds.paragraph = "none"
        ds.pacing_flavor = "snappy"
    else:
        ds.bubble_count = 1
        ds.send_mode = "single"
        ds.paragraph = "micro"
        ds.pacing_flavor = "neutral"
    # Cap emoji intensity by tier
    ds.emoji_level = min(ds.emoji_level, _tier_emoji_cap(inp.profile.tier))
    return ds

_topics_re = [
    (re.compile(r"\bfish(ing|er|)\b", re.I), "his fishing trip tomorrow; playful jealous angle"),
    (re.compile(r"\bgym|workout|lift\b", re.I), "his gym session; admiring + playful challenge"),
    (re.compile(r"\b(bday|birthday)\b", re.I), "his upcoming birthday; make him feel special"),
    (re.compile(r"\btrip|flight|travel|airport\b", re.I), "his trip plans; warm check-in + tease about missing you"),
    (re.compile(r"\bwork|shift|meeting\b", re.I), "his workday; supportive + a tiny flirty hook"),
    (re.compile(r"\btomorrow|tonight\b", re.I), "the near-time plan he mentioned; be specific & responsive"),
]

def _extract_talk_about(inp: BrainInput, limit: int = 2) -> List[str]:
    lines = [m.text for m in inp.messages.fan_last][-8:] + [m.text for m in inp.messages.creator_last][-8:]
    lines = [x for x in lines if x]
    found = []
    joined = " \n ".join(lines)
    for rx, hint in _topics_re:
        if rx.search(joined):
            found.append(hint)
    # memory crumbs
    if inp.memory and inp.memory.storybook:
        found.append(f"callback to earlier: {inp.memory.storybook[:80]}")
    if not found:
        found.append("reflect his last topic in flirty way")
    return found[:limit]

def _mirroring(inp: BrainInput) -> Mirroring:
    fp = inp.signals.style_fp or {}
    ex_rate = fp.get("exclaim_rate", 0.0)
    return Mirroring(
        use_emoji=fp.get("emoji_rate", 0.0) >= 0.05,
        exclaimation_tolerance="med" if ex_rate >= 0.15 else "low",
        question_echo=inp.signals.question_density >= 0.5,
        lexical_tone_hint="warm" if inp.signals.sentiment_score >= 0 else "soft",
    )

def _writer_style(inp: BrainInput) -> WriterStyle:
    return WriterStyle(max_chars=220, no_price=True, one_question_max=True)

def _pack_of(lines: List[str], mode: str) -> Pack:
    return Pack(send_mode=mode, bubbles=[{"text": t} for t in lines])  # type: ignore

def plan_candidates(inp: BrainInput, brief) -> List[Candidate]:
    ds = _build_delivery_style(inp)
    talk_about = _extract_talk_about(inp)
    mir = _mirroring(inp)
    ws = _writer_style(inp)

    # Base lines (writer will rewrite using writer_instructions)
    tease_lines = ["mmm I can't stop picturing you…", "tell me one more detail 😈"] if ds.bubble_count == 2 else ["mmm I can't stop picturing you… tell me one more detail 😈"]
    rapport_lines = ["that made me smile 😌", "what was the best part of it?"] if ds.bubble_count == 2 else ["that made me smile 😌 what was the best part of it?"]
    ppv_lines = ["Okay don't lie… you want the full thing 😏", "say the word and I’ll send it 👀"] if ds.bubble_count == 2 else ["Okay don't lie… you want the full thing 😏 say the word and I’ll send it 👀"]

    wi_common = dict(
        tone="playful",
        angle="light tease + one question" if brief.mission in ("soft_tease","rapport_value_add") else "confident offer",
        talk_about=talk_about,
        petnames=[],
        delivery_style=ds,
        mirroring=mir,
        style=ws,
    )
    cands: List[Candidate] = []

    # Candidate: soft tease
    cands.append(Candidate(
        id="soft_tease_v1",
        pack=_pack_of(tease_lines, ds.send_mode),
        forecast=0.55 + 0.1*inp.signals.sentiment_score,
        wi=WriterInstructions(**wi_common)
    ))

    # Candidate: rapport value add
    cands.append(Candidate(
        id="rapport_value_add_v1",
        pack=_pack_of(rapport_lines, ds.send_mode),
        forecast=0.52 + 0.12*inp.signals.sentiment_score + 0.08*inp.signals.question_density,
        wi=WriterInstructions(**{**wi_common, "angle": "warm + one reciprocal question"})
    ))

    # Candidate: ppv offer (only if catalog & intent)
    if inp.catalog and inp.signals.price_intent >= 0.45:
        cands.append(Candidate(
            id="ppv_offer_v1",
            pack=_pack_of(ppv_lines, ds.send_mode),
            forecast=0.60 + 0.20*inp.signals.price_intent - 0.05*(1.0 - inp.signals.sentiment_score),
            wi=WriterInstructions(**{**wi_common, "angle": "playful confident nudge"})
        ))

    return cands
