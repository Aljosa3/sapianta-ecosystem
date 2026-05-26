"""Bounded read-only HTTP GET provider."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol
from urllib import error, parse, request

from aigol.runtime.transport.serialization import replay_hash


@dataclass(frozen=True)
class HttpTransportResponse:
    status_code: int
    body: bytes
    headers: dict[str, str]


class HttpGetTransport(Protocol):
    def get(self, url: str, timeout_seconds: float, max_bytes: int) -> HttpTransportResponse:
        ...


class UrlLibHttpGetTransport:
    """Standard-library transport with redirects disabled and bounded reads."""

    def get(self, url: str, timeout_seconds: float, max_bytes: int) -> HttpTransportResponse:
        opener = request.build_opener(_NoRedirectHandler)
        req = request.Request(url, method="GET", headers={"User-Agent": "AiGOL-ReadOnlyHttpGetProvider/1"})
        with opener.open(req, timeout=timeout_seconds) as response:
            body = response.read(max_bytes + 1)
            return HttpTransportResponse(
                status_code=int(response.status),
                body=body,
                headers={key.lower(): value for key, value in response.headers.items()},
            )


class _NoRedirectHandler(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        return None


class ReadOnlyHttpGetProvider:
    """GET-only outbound HTTP provider with explicit domain allowlists."""

    def __init__(self, allowed_hosts: list[str], transport: HttpGetTransport | None = None) -> None:
        self._allowed_hosts = frozenset(host.lower() for host in allowed_hosts)
        self._transport = transport or UrlLibHttpGetTransport()

    def fetch(self, url: str, max_bytes: int, timeout_seconds: float) -> dict[str, Any]:
        if not isinstance(max_bytes, int) or max_bytes < 0:
            return self._evidence("fetch", url, "", "", False, "FAIL_CLOSED", None, 0, timeout_seconds, "", "max_bytes must be non-negative")
        if not isinstance(timeout_seconds, (int, float)) or timeout_seconds <= 0:
            return self._evidence("fetch", url, "", "", False, "FAIL_CLOSED", None, 0, timeout_seconds, "", "timeout_seconds must be positive")
        try:
            normalized_url, hostname = self._normalize_allowed_url(url)
            response = self._transport.get(normalized_url, float(timeout_seconds), max_bytes)
            if 300 <= response.status_code < 400 or "location" in response.headers:
                return self._evidence(
                    "fetch",
                    url,
                    normalized_url,
                    hostname,
                    True,
                    "FAIL_CLOSED",
                    response.status_code,
                    0,
                    timeout_seconds,
                    "",
                    "redirects are rejected",
                )
            body = response.body[:max_bytes]
            return self._evidence(
                "fetch",
                url,
                normalized_url,
                hostname,
                True,
                "FETCHED",
                response.status_code,
                len(body),
                timeout_seconds,
                replay_hash({"bytes": body.hex()}),
                "bounded GET completed",
                content=body.decode("utf-8", errors="replace"),
            )
        except error.HTTPError as exc:
            if 300 <= exc.code < 400:
                reason = "redirects are rejected"
            else:
                reason = str(exc)
            return self._evidence("fetch", url, "", "", False, "FAIL_CLOSED", int(exc.code), 0, timeout_seconds, "", reason)
        except (OSError, ValueError) as exc:
            return self._evidence("fetch", url, "", "", False, "FAIL_CLOSED", None, 0, timeout_seconds, "", str(exc))

    def _normalize_allowed_url(self, url: str) -> tuple[str, str]:
        if not self._allowed_hosts:
            raise ValueError("domain allowlist is required")
        parsed = parse.urlsplit(url)
        if parsed.scheme != "https":
            raise ValueError("only https URLs are allowed")
        if not parsed.hostname:
            raise ValueError("hostname is required")
        hostname = parsed.hostname.lower()
        if hostname not in self._allowed_hosts:
            raise ValueError("hostname is outside allowlist")
        if parsed.username or parsed.password:
            raise ValueError("embedded credentials are rejected")
        if parsed.fragment:
            parsed = parsed._replace(fragment="")
        normalized_path = parsed.path or "/"
        normalized = parse.urlunsplit((parsed.scheme.lower(), parsed.netloc.lower(), normalized_path, parsed.query, ""))
        return normalized, hostname

    def _evidence(
        self,
        operation: str,
        requested_url: str,
        normalized_url: str,
        hostname: str,
        allowlisted: bool,
        status: str,
        http_status: int | None,
        bytes_received: int,
        timeout_seconds: float,
        content_hash: str,
        reason: str,
        **extra: Any,
    ) -> dict[str, Any]:
        evidence = {
            "operation": operation,
            "requested_url": requested_url,
            "normalized_url": normalized_url,
            "hostname": hostname,
            "allowlisted": allowlisted,
            "status": status,
            "http_status": http_status,
            "bytes_received": bytes_received,
            "timeout_seconds": timeout_seconds,
            "content_hash": content_hash,
            "reason": reason,
        }
        evidence.update(extra)
        evidence["evidence_hash"] = replay_hash(evidence)
        return evidence
