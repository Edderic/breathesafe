from mask_recommender import breathesafe_network


class DummyResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


class DummySession:
    def __init__(self):
        self.calls = []

    def get(self, url, headers=None, timeout=None):
        self.calls.append({"url": url, "headers": headers, "timeout": timeout})
        return DummyResponse({"fit_tests_with_facial_measurements": []})


def test_fetch_facial_measurements_fit_tests_uses_internal_route_when_token_present(monkeypatch):
    session = DummySession()
    monkeypatch.setenv("MASK_RECOMMENDER_INTERNAL_API_TOKEN", "secret-token")

    breathesafe_network.fetch_facial_measurements_fit_tests(
        base_url="https://www.breathesafe.xyz",
        session=session,
    )

    assert session.calls[0]["url"] == "https://www.breathesafe.xyz/internal/facial_measurements_fit_tests.json"
    assert session.calls[0]["headers"] == {"X-Breathesafe-Internal-Token": "secret-token"}


def test_fetch_facial_measurements_fit_tests_uses_public_route_without_token(monkeypatch):
    session = DummySession()
    monkeypatch.delenv("MASK_RECOMMENDER_INTERNAL_API_TOKEN", raising=False)

    breathesafe_network.fetch_facial_measurements_fit_tests(
        base_url="https://www.breathesafe.xyz",
        session=session,
    )

    assert session.calls[0]["url"] == "https://www.breathesafe.xyz/facial_measurements_fit_tests.json"
    assert session.calls[0]["headers"] is None
