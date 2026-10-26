"""Maintainer-only metadata fetch. Never downloads model weights."""

import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from urllib.request import urlopen


def fetch(url: str) -> dict:
    with urlopen(url, timeout=30) as response:
        return json.load(response)


def select_weights(files: list[dict]) -> list[dict]:
    """Prefer a complete artifact; never count both it and its equivalent shards."""
    full = [f for f in files if f["rfilename"].lower().endswith("q4_k_m.gguf")]
    if len(full) == 1:
        return full
    if len(full) > 1:
        raise ValueError("Ambiguous complete artifacts")
    shards = []
    indexes = []
    totals = set()
    for item in files:
        match = re.search(r"q4_k_m-(\d+)-of-(\d+)\.gguf$", item["rfilename"].lower())
        if match:
            shards.append(item)
            indexes.append(int(match[1]))
            totals.add(int(match[2]))
    if len(totals) != 1 or sorted(indexes) != list(range(1, next(iter(totals)) + 1)):
        raise ValueError("Incomplete or ambiguous shard set")
    return sorted(shards, key=lambda item: item["rfilename"])


def speech_entries() -> list[dict]:
    """Read publisher metadata only; the multilingual models are not downloaded."""
    repo = "ggerganov/whisper.cpp"
    info = fetch(f"https://huggingface.co/api/models/{repo}?blobs=true")
    if info.get("cardData", {}).get("license") != "mit":
        raise ValueError("Review Whisper artifact license")
    runtime_revision = "231638a0717b7822784297e5980965ffcec05810"
    upstream_revision = "86098128c0b4f24f0e2aa2994de830614b474227"
    runtime_source = f"https://github.com/ggml-org/whisper.cpp/blob/{runtime_revision}/README.md"
    entries = []
    for size, parameters, memory_mb in [
        ("tiny", 0.039, 273),
        ("base", 0.074, 388),
        ("small", 0.244, 852),
    ]:
        weight = next(w for w in info["siblings"] if w["rfilename"] == f"ggml-{size}.bin")
        entries.append(
            {
                "id": f"whisper-{size}-ggml",
                "name": f"Whisper {size} · multilíngue",
                "roles": ["asr"],
                "parameters_b": parameters,
                "runtime": "whisper.cpp",
                "license": "mit",
                "quantization": "F16/F32",
                "format": "GGML",
                "weight_bytes": weight["size"],
                "max_context": None,
                "os": ["Windows", "Linux", "Darwin"],
                "architectures": ["AMD64", "x86_64", "arm64", "aarch64"],
                "tool_calling_verified": False,
                "source": f"https://huggingface.co/{repo}/tree/{info['sha']}",
                "config_source": f"https://github.com/openai/whisper/blob/{upstream_revision}/README.md",
                "license_source": f"https://github.com/openai/whisper/blob/{upstream_revision}/LICENSE",
                "runtime_source": runtime_source,
                "revision": info["sha"],
                "artifacts": [
                    {
                        "file": weight["rfilename"],
                        "bytes": weight["size"],
                        "sha256": weight["lfs"]["sha256"],
                    }
                ],
                "memory_estimator": "published_asr",
                "published_memory_mb": memory_mb,
                "memory_source": runtime_source + "#memory-usage",
                "languages": ["multilingual", "pt"],
                "planning_notes": [
                    "Transcrição multilíngue; qualidade em português não medida localmente.",
                    "Estimativa para áudio em blocos de até 30 s, uma entrada por agente; "
                    "não cobre carregar gravações inteiras ou arquivos "
                    "arbitrariamente grandes em RAM.",
                    "Transcrição não inclui síntese de voz, microfone ou execução de comandos.",
                ],
                "verification": "publisher_metadata; no local inference benchmark",
            }
        )
    return entries


def main() -> None:
    entries = []
    for family, roles in [("Qwen2.5", ["conversation"]), ("Qwen2.5-Coder", ["coding"])]:
        for size in ["0.5", "1.5", "7"]:
            model = f"Qwen/{family}-{size}B-Instruct"
            repo = f"{model}-GGUF"
            info = fetch(f"https://huggingface.co/api/models/{repo}?blobs=true")
            base = fetch(f"https://huggingface.co/api/models/{model}")
            config = fetch(f"https://huggingface.co/{model}/resolve/{base['sha']}/config.json")
            weights = select_weights(info["siblings"])
            if not weights:
                raise ValueError(f"Missing Q4_K_M artifact: {repo}")
            license_id = info.get("cardData", {}).get("license")
            if license_id != "apache-2.0":
                raise ValueError(f"Review license: {repo}: {license_id}")
            entries.append(
                {
                    "id": repo.split("/")[1].lower() + "-q4_k_m",
                    "name": model,
                    "roles": roles,
                    "parameters_b": float(size),
                    "runtime": "llama.cpp",
                    "license": license_id,
                    "quantization": "Q4_K_M",
                    "weight_bytes": sum(weight["size"] for weight in weights),
                    "layers": config["num_hidden_layers"],
                    "kv_heads": config["num_key_value_heads"],
                    "head_dim": config["hidden_size"] // config["num_attention_heads"],
                    "max_context": config["max_position_embeddings"],
                    "os": ["Windows", "Linux", "Darwin"],
                    "architectures": ["AMD64", "x86_64", "arm64", "aarch64"],
                    "tool_calling_verified": False,
                    "source": f"https://huggingface.co/{repo}/tree/{info['sha']}",
                    "config_source": f"https://huggingface.co/{model}/blob/{base['sha']}/config.json",
                    "license_source": f"https://huggingface.co/{repo}/blob/{info['sha']}/LICENSE",
                    "revision": info["sha"],
                    "artifacts": [
                        {
                            "file": w["rfilename"],
                            "bytes": w["size"],
                            "sha256": w.get("lfs", {}).get("sha256"),
                        }
                        for w in weights
                    ],
                    "verification": "publisher_metadata; no local inference benchmark",
                }
            )
    entries.extend(speech_entries())
    payload = {
        "version": "2026-10-26.1",
        "retrieved_at": datetime.now(UTC).isoformat(),
        "runtime_source": "https://github.com/ggml-org/llama.cpp",
        "entries": entries,
    }
    target = Path(__file__).resolve().parents[1] / "src/zynvu/data/catalog.json"
    target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    print(f"Saved {len(entries)} metadata entries; sha256={digest}")


if __name__ == "__main__":
    main()
