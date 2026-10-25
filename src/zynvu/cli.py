import argparse
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import ValidationError

from zynvu.catalog import load_catalog
from zynvu.contracts import HardwareProfile, Requirements
from zynvu.engine import advise
from zynvu.export import report, scrub, validate_blueprint
from zynvu.hardware import diagnose
from zynvu.requirements import parse_goal


def read_json(path: str) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError("Objeto JSON esperado")
    return data


def emit(data: Any, path: str | None) -> None:
    content = json.dumps(scrub(data), indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    if path:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    else:
        print(content, end="")


def main(argv: list[str] | None = None) -> int:
    # Windows redirected stdout can default to a legacy code page. JSON is UTF-8.
    for stream in [sys.stdout, sys.stderr]:
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(prog="zynvu", description="Advisor local de arquitetura de IA")
    commands = parser.add_subparsers(dest="command", required=True)
    diagnostic = commands.add_parser("diagnose", help="Diagnosticar hardware local")
    diagnostic.add_argument("--out")
    commands.add_parser("catalog", help="Exibir catálogo offline")
    commands.add_parser("desktop", help="Abrir interface nativa local")
    api = commands.add_parser("serve", help="API loopback autenticada por ZYNVU_API_TOKEN")
    api.add_argument("--port", type=int, default=8765)
    parse = commands.add_parser("parse", help="Revisar requisitos extraídos")
    parse.add_argument("goal")
    parse.add_argument("--out")
    recommendation = commands.add_parser("advise", help="Gerar Blueprint e relatório")
    source = recommendation.add_mutually_exclusive_group(required=True)
    source.add_argument("--goal")
    source.add_argument("--requirements")
    recommendation.add_argument("--hardware", help="Perfil JSON; omitido: diagnóstico real")
    recommendation.add_argument("--policy", help="Política de executores JSON")
    recommendation.add_argument("--require-installed", action="store_true")
    recommendation.add_argument("--out")
    recommendation.add_argument("--report")
    validate = commands.add_parser("validate", help="Validar Blueprint JSON")
    validate.add_argument("path")
    args = parser.parse_args(argv)
    try:
        if args.command == "desktop":
            from zynvu.desktop import launch

            launch()
        elif args.command == "serve":
            from zynvu.api import serve

            serve(args.port)
        elif args.command == "diagnose":
            emit(diagnose().to_dict(), args.out)
        elif args.command == "catalog":
            emit(load_catalog(), None)
        elif args.command == "parse":
            emit(parse_goal(args.goal).to_dict(), args.out)
        elif args.command == "validate":
            validate_blueprint(read_json(args.path))
            print("Blueprint válido.")
        elif args.command == "advise":
            req = (
                read_json(args.requirements)
                if args.requirements
                else parse_goal(args.goal).to_dict()
            )
            if args.policy:
                policy = read_json(args.policy)
                for key in ["allowed_interface_executors", "denied_interface_executors"]:
                    if key not in policy:
                        raise ValueError(f"Política deve declarar {key}")
                    req[key] = policy[key]
            if args.require_installed:
                req["require_installed"] = True
            hardware = HardwareProfile(**read_json(args.hardware)) if args.hardware else diagnose()
            blueprint = advise(Requirements(**req), hardware)
            if args.out and args.report and Path(args.out).resolve() == Path(args.report).resolve():
                raise ValueError("Blueprint e relatório precisam de caminhos diferentes")
            emit(blueprint, args.out)
            if args.report:
                target = Path(args.report)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(report(blueprint), encoding="utf-8")
            return (
                3 if all(r["status"] == "not_feasible" for r in blueprint["recommendations"]) else 0
            )
    except (OSError, ValueError, TypeError, ValidationError):
        # Do not echo inputs/exception values, which might contain credentials.
        print(
            "Entrada inválida ou arquivo indisponível. Verifique os campos e caminhos.",
            file=sys.stderr,
        )
        return 2
    return 0
