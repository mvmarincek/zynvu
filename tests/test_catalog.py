import pytest

from scripts.refresh_catalog import select_weights
from zynvu.catalog import load_catalog


def test_complete_file_and_shards_are_alternatives():
    files = [
        {"rfilename": "model-q4_k_m.gguf", "size": 100},
        {"rfilename": "model-q4_k_m-00001-of-00002.gguf", "size": 70},
        {"rfilename": "model-q4_k_m-00002-of-00002.gguf", "size": 30},
    ]
    assert sum(item["size"] for item in select_weights(files)) == 100
    assert sum(item["size"] for item in select_weights(files[1:])) == 100
    with pytest.raises(ValueError):
        select_weights(files[1:2])


def test_catalog_has_consistent_verified_artifact_metadata():
    for entry in load_catalog()["entries"]:
        assert entry["weight_bytes"] == sum(part["bytes"] for part in entry["artifacts"])
        assert len(entry["revision"]) == 40
        assert all(len(part["sha256"]) == 64 for part in entry["artifacts"])
        assert 0 < entry["weight_bytes"] < entry["parameters_b"] * 4 * 1024**3
        assert entry["license"] in {"apache-2.0", "mit"}


def test_speech_models_are_multilingual_and_have_separate_memory_provenance():
    speech = [entry for entry in load_catalog()["entries"] if "asr" in entry["roles"]]
    assert len(speech) == 3
    for entry in speech:
        assert "pt" in entry["languages"]
        assert ".en" not in entry["artifacts"][0]["file"]
        assert entry["max_context"] is None
        assert entry["memory_estimator"] == "published_asr"
        assert entry["published_memory_mb"] > entry["weight_bytes"] / 1_000_000
        assert entry["memory_source"].startswith("https://github.com/ggml-org/whisper.cpp/")
