import json
from pathlib import Path
from jsonschema import Draft202012Validator

root = Path(__file__).resolve().parents[1]
in_schema = json.loads((root/"contracts"/"strategist_in.schema.json").read_text())
out_schema = json.loads((root/"contracts"/"strategist_out.schema.json").read_text())
Draft202012Validator.check_schema(in_schema)
Draft202012Validator.check_schema(out_schema)
print("Strategist schemas: OK")
