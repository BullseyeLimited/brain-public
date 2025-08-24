# Brain

FastAPI sidecar that decides what to send next. Two main routes:

- `POST /suggest?view=admin|operator` – sidecar contract used by the backend.
- `POST /auto_decide` – convenience: send raw messages; the brain derives signals for you and decides.

Run:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

Quick test:

```bash
curl -s -X POST "http://127.0.0.1:8001/suggest?view=admin"   -H "Content-Type: application/json"   -d @app/demo/sample_bundle.json | jq .
```

Design highlights:
- **No waits** in message bubbles (operator will paste; no enforced delay).
- PPV pricing respects `budget` floors/ceilings and catalog.
- Persona hints are returned so your writer can adapt tone and emoji usage.
- Deterministic, lightweight heuristics; safe to run offline.
