"""Unit tests for 429 handling: retry with backoff, Retry-After, and RateLimitError."""

import json

import pytest
from requests import Response as RequestsResponse
from requests.hooks import dispatch_hook

import runzero.client._http.io as io
from runzero.client import Client
from runzero.client.errors import ClientError, RateLimitError


def _response(status: int, body: dict, headers: dict | None = None) -> RequestsResponse:
    resp = RequestsResponse()
    resp.status_code = status
    resp.reason = "Too Many Requests" if status == 429 else "OK"
    resp.headers.update({"Content-Type": "application/json"})
    resp.headers.update(headers or {})
    resp._content = json.dumps(body).encode()  # pylint: disable=protected-access
    return resp


class _FakeSession:
    """Serves canned responses in order and runs the prepared request's response hooks like requests does."""

    queue: list = []
    sent: int = 0

    def send(self, prepared, **kwargs):
        _FakeSession.sent += 1
        resp = _FakeSession.queue.pop(0)
        resp.request = prepared
        return dispatch_hook("response", prepared.hooks, resp, **kwargs)


@pytest.fixture
def fake_http(monkeypatch):
    waits: list = []
    _FakeSession.queue = []
    _FakeSession.sent = 0
    monkeypatch.setattr(io, "Session", _FakeSession)
    monkeypatch.setattr(io, "_sleep", waits.append)
    yield _FakeSession, waits


def _client(**kwargs) -> Client:
    return Client(org_key="OT" + "0" * 28, server_url="https://console.local", **kwargs)


def test_retries_then_succeeds_honoring_retry_after(fake_http):
    session, waits = fake_http
    session.queue = [
        _response(429, {"error": "slow down"}, {"Retry-After": "7"}),
        _response(429, {"error": "slow down"}, {"Retry-After": "2"}),
        _response(200, {"ok": True}),
    ]
    resp = _client().execute("GET", "api/v1.0/org")
    assert resp.status_code == 200
    assert resp.json_obj == {"ok": True}
    assert session.sent == 3
    assert waits == [7.0, 2.0], "the server's Retry-After wins over backoff"


def test_backoff_doubles_without_retry_after(fake_http, monkeypatch):
    session, waits = fake_http
    monkeypatch.setattr(io.random, "uniform", lambda *_: 0.0)
    session.queue = [
        _response(429, {"error": "slow down"}),
        _response(429, {"error": "slow down"}),
        _response(200, {"ok": True}),
    ]
    _client(rate_limit_backoff_seconds=0.5).execute("GET", "api/v1.0/org")
    assert waits == [0.5, 1.0]


def test_raises_rate_limit_error_after_retries(fake_http):
    session, waits = fake_http
    session.queue = [_response(429, {"error": "slow down"}, {"Retry-After": "1"}) for _ in range(3)]
    with pytest.raises(RateLimitError) as exc:
        _client(rate_limit_retries=2).execute("GET", "api/v1.0/org")
    assert session.sent == 3
    assert waits == [1.0, 1.0]
    assert exc.value.retry_after == 1
    assert isinstance(exc.value, ClientError), "existing ClientError handlers still catch rate limits"


def test_zero_retries_raises_immediately(fake_http):
    session, waits = fake_http
    session.queue = [_response(429, {"error": "slow down"})]
    with pytest.raises(RateLimitError):
        _client(rate_limit_retries=0).execute("GET", "api/v1.0/org")
    assert session.sent == 1
    assert waits == []


def test_retry_after_is_capped():
    assert io.rate_limit_wait_seconds(0, 10_000, 1.0) == io.MAX_RATE_LIMIT_WAIT_SECONDS
    assert io.rate_limit_wait_seconds(0, 3, 1.0) == 3.0
    assert io.rate_limit_wait_seconds(20, None, 1.0) == io.MAX_RATE_LIMIT_WAIT_SECONDS


def test_client_rejects_negative_retry_settings():
    with pytest.raises(ValueError):
        _client(rate_limit_retries=-1)
    with pytest.raises(ValueError):
        _client(rate_limit_backoff_seconds=-1)
    assert _client().rate_limit_retries == io.DEFAULT_RATE_LIMIT_RETRIES


def test_error_handler_does_not_stack_across_retries(fake_http):
    """A retried request registers the error handler once per attempt, not cumulatively."""
    session, _ = fake_http
    session.queue = [_response(429, {"error": "slow down"}, {"Retry-After": "0"}), _response(200, {"ok": True})]
    request = io.Request(url="https://console.local/x", token="t", method="GET", rate_limit_retries=1)
    request.execute()
    assert request.handlers == []
