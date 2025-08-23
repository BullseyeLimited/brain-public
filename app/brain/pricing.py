from __future__ import annotations
from typing import List, Dict, Optional

def choose_price(budget: Dict, catalog: Optional[List[Dict]] = None) -> float:
    floor = float(budget.get("price_floor", 9.0))
    ceil  = float(budget.get("price_ceiling", 22.0))
    step  = float(budget.get("price_step", 1.0))

    base = None
    if catalog:
        # pick the cheapest viable item by default
        base = min((float(x.get("base_price", ceil)) for x in catalog), default=None)
    price = base if base is not None else floor
    # clamp and align to step
    price = min(max(price, floor), ceil)
    # align to step
    price = round((price/step)) * step
    return float(price)
