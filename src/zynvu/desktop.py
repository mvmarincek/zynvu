"""Offline browser UI, isolated from the token-authenticated SDK API."""

import hmac
import json
import secrets
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.resources import files
from typing import Any

from jsonschema import ValidationError

from zynvu.catalog import load_catalog
from zynvu.contracts import HardwareProfile, Requirements
from zynvu.engine import advise
from zynvu.export import report, scrub
from zynvu.hardware import diagnose
from zynvu.requirements import parse_goal

ASSETS = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/app.css": ("app.css", "text/css; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
}


def make_desktop_server(port: int = 0) -> ThreadingHTTPServer:
    """Loopback only; fresh per-process nonce protects every data route."""
    nonce = secrets.token_urlsafe(32)

    class Handler(BaseHTTPRequestHandler):
        def setup(self) -> None:
            super().setup()
            self.connection.settimeout(15)

        def log_message(self, format: str, *args: Any) -> None:
            pass

        def respond(self, code: int, payload: bytes, content_type: str) -> None:
            self.send_response(code)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header(
                "Content-Security-Policy",
                "default-src 'none'; script-src 'self'; style-src 'self'; "
                "connect-src 'self'; img-src 'self' data:; font-src 'self'; "
                "base-uri 'none'; form-action 'none'; frame-ancestors 'none'",
            )
            self.end_headers()
            self.wfile.write(payload)

        def reply(self, code: int, payload: Any) -> None:
            self.respond(
                code,
                json.dumps(payload, ensure_ascii=False, allow_nan=False).encode(),
                "application/json; charset=utf-8",
            )

        def local_request(self, *, protected: bool = False) -> bool:
            origin = f"http://127.0.0.1:{server.server_port}"
            if (
                self.headers.get("Host") != origin.removeprefix("http://")
                or self.headers.get("Sec-Fetch-Site") == "cross-site"
                or self.headers.get("Origin") not in {None, origin}
            ):
                self.reply(403, {"error": "Origem não permitida."})
                return False
            supplied = self.headers.get("X-Zynvu-Session", "").encode()
            if protected and not hmac.compare_digest(supplied, nonce.encode()):
                self.reply(401, {"error": "Sessão expirada. Reabra a interface local."})
                return False
            return True

        def do_GET(self) -> None:
            if not self.local_request():
                return
            if self.path in ASSETS:
                name, content_type = ASSETS[self.path]
                asset = files("zynvu").joinpath(f"ui/{name}").read_bytes()
                if name == "index.html":
                    asset = asset.replace(b"__ZYNVU_SESSION__", nonce.encode("ascii"))
                self.respond(200, asset, content_type)
            elif self.path == "/ui/catalog":
                if self.local_request(protected=True):
                    self.reply(200, load_catalog())
            else:
                self.reply(404, {"error": "Recurso não encontrado."})

        def do_POST(self) -> None:
            if not self.local_request(protected=True):
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= 65536 or self.headers.get("Transfer-Encoding"):
                    self.reply(413, {"error": "Solicitação excede o tamanho permitido."})
                    return
                if self.headers.get_content_type() != "application/json":
                    self.reply(415, {"error": "Envie um objeto JSON."})
                    return
                payload = json.loads(self.rfile.read(length))
                if not isinstance(payload, dict):
                    raise ValueError("Object expected")
                if self.path == "/ui/hardware":
                    self.reply(200, scrub(diagnose().to_dict()))
                elif self.path == "/ui/parse":
                    goal = payload["goal"]
                    if not isinstance(goal, str):
                        raise ValueError("Text expected")
                    self.reply(200, scrub(parse_goal(goal).to_dict()))
                elif self.path == "/ui/requirements":
                    self.reply(200, scrub(Requirements(**payload).to_dict()))
                elif self.path == "/ui/advise":
                    req = Requirements(**payload["requirements"])
                    hardware = HardwareProfile(**payload["hardware"])
                    blueprint = advise(req, hardware)
                    self.reply(200, {"blueprint": blueprint, "report": report(blueprint)})
                else:
                    self.reply(404, {"error": "Recurso não encontrado."})
            except (ValueError, TypeError, KeyError, ValidationError):
                self.reply(400, {"error": "Revise o objetivo, as capacidades e os requisitos."})
            except OSError:
                self.reply(503, {"error": "Diagnóstico indisponível. Tente novamente."})

    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    return server


def launch(port: int = 0, *, open_browser: bool = True) -> None:
    with make_desktop_server(port) as server:
        url = f"http://127.0.0.1:{server.server_port}"
        print(f"ZYNVU Studio em {url} · Ctrl+C para encerrar.")
        if open_browser:
            webbrowser.open(url)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
