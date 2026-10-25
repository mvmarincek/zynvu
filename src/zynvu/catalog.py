import json
from importlib.resources import files
from typing import Any


def load_catalog() -> dict[str, Any]:
    catalog: dict[str, Any] = json.loads(
        files("zynvu").joinpath("data/catalog.json").read_text("utf-8")
    )
    return catalog
