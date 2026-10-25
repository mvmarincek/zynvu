"""Optional authenticated loopback API. No CORS or external binding."""

import hmac
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from zynvu.catalog import load_catalog
from zynvu.contracts import HardwareProfile, Requirements
from zynvu.engine import advise
from zynvu.hardware import diagnose

MAX_BODY = 64 * 1024


def make_server(port: int, token: str) -> ThreadingHTTPServer:
    if len(token) < 32:
        raise ValueError("ZYNVU_API_TOKEN deve ter pelo menos 32 caracteres")

    class Handler(BaseHTTPRequestHandler):
        def setup(self) -> None:
            super().setup()
            self.connection.settimeout(10)

        def log_message(self, format: str, *args: Any) -> None:
            pass  # No request payloads, tokens or hardware facts in access logs.

        def reply(self, code: int, data: Any) -> None:
            payload = json.dumps(data, ensure_ascii=False, allow_nan=False).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(payload)

        def authorized(self) -> bool:
            # Browser origins are deliberately unsupported; SDK/API uses bearer authentication.
            if self.headers.get("Origin"):
                self.reply(403, {"error": "browser_origin_denied"})
                return False
            supplied = self.headers.get("Authorization", "").encode("utf-8")
            if not hmac.compare_digest(supplied, f"Bearer {token}".encode()):
                self.reply(401, {"error": "unauthorized"})
                return False
            return True

        def do_GET(self) -> None:
            if not self.authorized():
                return
            if self.path == "/v1/catalog":
                self.reply(200, load_catalog())
            elif self.path == "/v1/hardware":
                self.reply(200, diagnose().to_dict())
            else:
                self.reply(404, {"error": "not_found"})

        def do_POST(self) -> None:
            if not self.authorized():
                return
            if self.path != "/v1/advise":
                self.reply(404, {"error": "not_found"})
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= MAX_BODY or self.headers.get("Transfer-Encoding"):
                    self.reply(413, {"error": "body_size"})
                    return
                if self.headers.get_content_type() != "application/json":
                    self.reply(415, {"error": "json_required"})
                    return
                payload = json.loads(self.rfile.read(length))
                if not isinstance(payload, dict) or set(payload) != {"requirements", "hardware"}:
                    raise ValueError("Expected requirements and hardware")
                result = advise(
                    Requirements(**payload["requirements"]), HardwareProfile(**payload["hardware"])
                )
                self.reply(200, result)
            except (ValueError, TypeError, KeyError):
                self.reply(400, {"error": "invalid_input"})

    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


def serve(port: int) -> None:
    with make_server(port, os.environ.get("ZYNVU_API_TOKEN", "")) as server:
        print(f"API local em http://127.0.0.1:{server.server_port}; Ctrl+C para encerrar.")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
