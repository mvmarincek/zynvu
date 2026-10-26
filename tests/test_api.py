import json
import threading
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from zynvu.api import make_server

TOKEN = "fixture-token-" + "x" * 32


@pytest.fixture
def api():
    server = make_server(0, TOKEN)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()
    server.server_close()
    thread.join(timeout=3)


def test_auth_and_origin(api):
    for headers, status in [
        ({}, 401),
        ({"Authorization": "Bearer wrong"}, 401),
        ({"Authorization": f"Bearer {TOKEN}", "Origin": "https://other.test"}, 403),
    ]:
        with pytest.raises(HTTPError) as error:
            urlopen(Request(api + "/v1/catalog", headers=headers), timeout=5)
        assert error.value.code == status
    with urlopen(
        Request(api + "/v1/catalog", headers={"Authorization": f"Bearer {TOKEN}"}), timeout=5
    ) as response:
        assert len(json.load(response)["entries"]) == 9
        assert response.headers["Cache-Control"] == "no-store"


def test_advice_roundtrip(api):
    data = {
        "requirements": {"user_goal": "chat"},
        "hardware": {
            "source": "fixture",
            "observed_at": "2026-10-25T00:00:00Z",
            "os": "Windows",
            "cpu": "fixture",
            "ram_gb": 8,
        },
    }
    request = Request(
        api + "/v1/advise",
        data=json.dumps(data).encode(),
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
        },
    )
    with urlopen(request, timeout=5) as response:
        assert json.load(response)["recommendations"][0]["status"] == "candidate"


def test_bad_token_and_payload(api):
    with pytest.raises(ValueError):
        make_server(0, "short")
    request = Request(
        api + "/v1/advise",
        data=b'{"secret":"hidden"}',
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
        },
    )
    with pytest.raises(HTTPError) as error:
        urlopen(request, timeout=5)
    assert error.value.code == 400
    assert b"hidden" not in error.value.read()
