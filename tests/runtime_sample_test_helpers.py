import json
from pathlib import Path

from sema.registry.codec import default_codec


RUNTIME_SAMPLES = Path(__file__).parent / "runtime_samples"


def load_runtime_payload(relative_path: str) -> dict:
    sample_path = RUNTIME_SAMPLES / relative_path
    envelope = json.loads(sample_path.read_text())
    return envelope["Payload"]


def decode_runtime_payload(relative_path: str):
    return default_codec.from_dict(load_runtime_payload(relative_path))
