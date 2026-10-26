import json
import re
import threading
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from zynvu.desktop import make_desktop_server


@pytest.fixture
def studio():
    server = make_desktop_server()
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    url = f"http://127.0.0.1:{server.server_port}"
    with urlopen(url, timeout=5) as response:
        html = response.read().decode("utf-8-sig")
        assert "frame-ancestors 'none'" in response.headers["Content-Security-Policy"]
    nonce = re.search(r'name="zynvu-session" content="([^"]+)"', html)[1]
    yield url, nonce
    server.shutdown()
    server.server_close()
    thread.join(timeout=3)


def test_studio_bundles_assets_and_catalog(studio):
    url, nonce = studio
    for path in ["/app.js", "/app.css"]:
        with urlopen(url + path, timeout=5) as response:
            assert response.status == 200
            assert response.headers["Cache-Control"] == "no-store"
    with urlopen(
        Request(url + "/ui/catalog", headers={"X-Zynvu-Session": nonce}), timeout=5
    ) as response:
        assert len(json.load(response)["entries"]) == 6


@pytest.mark.parametrize(
    "headers,status",
    [
        ({}, 401),
        ({"Origin": "https://other.test"}, 403),
        ({"Host": "malicious.test"}, 403),
        ({"Sec-Fetch-Site": "cross-site"}, 403),
    ],
)
def test_local_data_protected_from_cross_site_requests(studio, headers, status):
    url, _ = studio
    with pytest.raises(HTTPError) as error:
        urlopen(
            Request(
                url + "/ui/hardware",
                data=b"{}",
                headers={"Content-Type": "application/json", **headers},
            ),
            timeout=5,
        )
    assert error.value.code == status


def test_studio_parse_advise_and_report(studio):
    url, nonce = studio

    def post(route, payload):
        request = Request(
            url + "/ui/" + route,
            data=json.dumps(payload).encode(),
            headers={
                "X-Zynvu-Session": nonce,
                "Content-Type": "application/json",
                "Origin": url,
            },
        )
        with urlopen(request, timeout=5) as response:
            return json.load(response)

    requirements = post("parse", {"goal": "Conversar e programar"})
    assert "coding" in requirements["capabilities"]
    result = post(
        "advise",
        {
            "requirements": requirements,
            "hardware": {
                "source": "fixture",
                "observed_at": "2026-10-25T00:00:00Z",
                "os": "Windows",
                "cpu": "fixture",
                "ram_gb": 8,
            },
        },
    )
    assert len(result["blueprint"]["recommendations"]) == 3
    assert "Pico estimado" in result["report"]
    with pytest.raises(HTTPError) as error:
        post("requirements", {"secret": "not-to-be-echoed"})
    assert b"not-to-be-echoed" not in error.value.read()
