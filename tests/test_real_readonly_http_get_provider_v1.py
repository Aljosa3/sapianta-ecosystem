"""Tests for REAL_READONLY_HTTP_GET_PROVIDER_V1."""

from __future__ import annotations

import inspect
import socket

from aigol.runtime.providers import HttpTransportResponse, ReadOnlyHttpGetProvider


class FakeTransport:
    def __init__(self, response: HttpTransportResponse | None = None, exc: Exception | None = None) -> None:
        self.response = response or HttpTransportResponse(status_code=200, body=b"hello http", headers={})
        self.exc = exc
        self.calls: list[tuple[str, float, int]] = []

    def get(self, url: str, timeout_seconds: float, max_bytes: int) -> HttpTransportResponse:
        self.calls.append((url, timeout_seconds, max_bytes))
        if self.exc:
            raise self.exc
        return self.response


def _provider(transport: FakeTransport | None = None) -> ReadOnlyHttpGetProvider:
    return ReadOnlyHttpGetProvider(["example.com"], transport=transport or FakeTransport())


def test_allowed_https_request() -> None:
    transport = FakeTransport()

    evidence = _provider(transport).fetch("https://example.com/path?q=1", max_bytes=20, timeout_seconds=2)

    assert evidence["status"] == "FETCHED"
    assert evidence["allowlisted"] is True
    assert evidence["hostname"] == "example.com"
    assert evidence["normalized_url"] == "https://example.com/path?q=1"
    assert evidence["http_status"] == 200
    assert evidence["bytes_received"] == len("hello http")
    assert transport.calls == [("https://example.com/path?q=1", 2.0, 20)]


def test_blocked_non_https_request() -> None:
    transport = FakeTransport()

    evidence = _provider(transport).fetch("http://example.com/", max_bytes=20, timeout_seconds=2)

    assert evidence["status"] == "FAIL_CLOSED"
    assert evidence["allowlisted"] is False
    assert "https" in evidence["reason"]
    assert transport.calls == []


def test_blocked_non_allowlisted_host() -> None:
    transport = FakeTransport()

    evidence = _provider(transport).fetch("https://not-example.com/", max_bytes=20, timeout_seconds=2)

    assert evidence["status"] == "FAIL_CLOSED"
    assert "outside allowlist" in evidence["reason"]
    assert transport.calls == []


def test_timeout_enforcement() -> None:
    transport = FakeTransport(exc=TimeoutError("timed out"))

    evidence = _provider(transport).fetch("https://example.com/", max_bytes=20, timeout_seconds=1)

    assert evidence["status"] == "FAIL_CLOSED"
    assert evidence["timeout_seconds"] == 1
    assert "timed out" in evidence["reason"]
    assert transport.calls == [("https://example.com/", 1.0, 20)]


def test_max_bytes_enforcement() -> None:
    transport = FakeTransport(HttpTransportResponse(status_code=200, body=b"0123456789", headers={}))

    evidence = _provider(transport).fetch("https://example.com/", max_bytes=4, timeout_seconds=2)

    assert evidence["status"] == "FETCHED"
    assert evidence["bytes_received"] == 4
    assert evidence["content"] == "0123"


def test_redirect_rejection() -> None:
    transport = FakeTransport(HttpTransportResponse(status_code=302, body=b"", headers={"location": "https://example.com/next"}))

    evidence = _provider(transport).fetch("https://example.com/", max_bytes=20, timeout_seconds=2)

    assert evidence["status"] == "FAIL_CLOSED"
    assert evidence["http_status"] == 302
    assert "redirects" in evidence["reason"]


def test_deterministic_evidence_generation() -> None:
    first = _provider().fetch("https://example.com/", max_bytes=20, timeout_seconds=2)
    second = _provider().fetch("https://example.com/", max_bytes=20, timeout_seconds=2)

    assert first == second
    assert set(first) >= {
        "operation",
        "requested_url",
        "normalized_url",
        "hostname",
        "allowlisted",
        "status",
        "http_status",
        "bytes_received",
        "timeout_seconds",
        "content_hash",
        "evidence_hash",
        "reason",
    }


def test_fail_closed_invalid_url_handling() -> None:
    evidence = _provider().fetch("not-a-url", max_bytes=20, timeout_seconds=2)

    assert evidence["status"] == "FAIL_CLOSED"
    assert "https" in evidence["reason"] or "hostname" in evidence["reason"]


def test_missing_allowlist_fails_closed() -> None:
    evidence = ReadOnlyHttpGetProvider([], transport=FakeTransport()).fetch("https://example.com/", 20, 2)

    assert evidence["status"] == "FAIL_CLOSED"
    assert "allowlist" in evidence["reason"]


def test_no_mutation_async_retry_crawl_shell_surface() -> None:
    public_methods = {
        name
        for name, value in inspect.getmembers(ReadOnlyHttpGetProvider, predicate=inspect.isfunction)
        if not name.startswith("_")
    }
    source = inspect.getsource(ReadOnlyHttpGetProvider)

    assert public_methods == {"fetch"}
    assert "POST" not in source
    assert "PUT" not in source
    assert "PATCH" not in source
    assert "DELETE" not in source
    assert "async" not in source
    assert "retry" not in source.lower()
    assert "subprocess" not in source
    assert "system(" not in source
    assert "crawl" not in source.lower()
    assert socket
