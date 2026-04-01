# api/main.py
import yaml
from pathlib import Path

# Load registry from YAML at startup
registry_path = Path("../type_definitions/registry.yaml")
with open(registry_path) as f:
    REGISTRY = yaml.safe_load(f)

@app.get("/types")
async def list_types():
    return REGISTRY["types"]