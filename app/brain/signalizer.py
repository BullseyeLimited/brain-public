from __future__ import annotations
import re
from typing import List
from .contracts import MessageLine, Signals

_emoji_re = re.compile(r"[\U0001F300-\U0001FAFF]")
_q_re = re.compile(r"\?+")
_exc_re = re.compile(r"!+")
_imperatives = {"send", "show", "tell", "gimme", "give", "call", "answer", "reply", "prove"}

def _rate(n: int, d: int) -> float:
    return 0.0 if d <= 0 else max(0.0, min(1.0, n / d))

def _sentiment_guess(text: str) -> float:
    t = text.lower()
    pos = sum(t.count(k) for k in ["love", "like", "sweet", "cute", "nice", "great", "good", "😍", "🥰"])
    neg = sum(t.count(k) for k in ["hate", "mad", "angry", "annoy", "bad", "worst", "🙄", "😠"])
    return max(-1.0, min(1.0, (pos - neg) / 5.0))

def derive_signals(fan_last: List[MessageLine]) -> Signals:
    texts = [m.text for m in fan_last][-8:]
    total = len(texts)

    emoji_hits = sum(1 for t in texts if _emoji_re.search(t))
    q_hits = sum(1 for t in texts if _q_re.search(t))
    exc_hits = sum(1 for t in texts if _exc_re.search(t))
    imper = sum(any(w in _imperatives for w in re.findall(r"[a-z']+", t.lower())) for t in texts)

    avg_chars = sum(len(t) for t in texts) / total if total else 0
    style_fp = {
        "avg_chars": float(avg_chars),
        "emoji_rate": _rate(emoji_hits, total),
        "question_rate": _rate(q_hits, total),
        "exclaim_rate": _rate(exc_hits, total),
    }

    # Basic urgency proxy: short bursts + questions + imperatives
    burst = sum(1 for t in texts[-3:] if len(t) <= 40)
    reply_urgency = max(0.0, min(1.0, 0.25 + 0.18*_rate(q_hits, total) + 0.15*_rate(imper, total) + 0.18*_rate(burst, 3)))

    sentiment = 0.0
    if texts:
        sentiment = sum(_sentiment_guess(t) for t in texts[-3:]) / min(3, len(texts))

    # very rough proxy for price intent: words that hint willingness to buy
    price_words = ["price", "cost", "how much", "send pic", "send video", "pay", "tip", "buy"]
    price_intent = 0.0
    joined = " ".join(texts).lower()
    if any(w in joined for w in price_words):
        price_intent = 0.55 + 0.15*_rate(imper, total) + 0.1*_rate(q_hits, total)
        price_intent = min(1.0, price_intent)

    question_density = _rate(q_hits, total)
    interruption = (burst >= 2 and q_hits >= 1)

    return Signals(
        reply_urgency=reply_urgency,
        sentiment_score=sentiment,
        price_intent=price_intent,
        fan_burst_count=burst,
        interruption=interruption,
        question_density=question_density,
        imperative_hits=imper,
        style_fp=style_fp,
    )
