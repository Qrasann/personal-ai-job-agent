from __future__ import annotations

import errno
import socket
import ssl

import httpx

TRANSPORT_ERROR_TYPES = (httpx.TransportError, socket.gaierror, ssl.SSLError)


def transport_failure_category(exc: BaseException) -> str:
    """Describe typed causes only; never inspect exception text or request URLs."""
    chain: list[BaseException] = []
    seen: set[int] = set()
    current: BaseException | None = exc
    while current is not None and id(current) not in seen and len(chain) < 16:
        seen.add(id(current))
        chain.append(current)
        if current.__cause__ is not None:
            current = current.__cause__
            continue
        wrapper_module = type(current).__module__.partition(".")[0]
        # httpcore/anyio deliberately suppress their lower-level context while
        # translating transport failures. That context is still the typed
        # network cause we need (for example SSLEOFError behind ConnectError).
        # Do not traverse suppressed context for application exceptions.
        if current.__suppress_context__ and wrapper_module not in {"httpcore", "anyio"}:
            current = None
        else:
            current = current.__context__
    for cause in reversed(chain):
        if isinstance(cause, socket.gaierror):
            return "dns"
        if isinstance(cause, ssl.SSLCertVerificationError):
            return "tls_certificate"
        if isinstance(cause, ssl.SSLError):
            return "tls"
        if isinstance(cause, OSError):
            if cause.errno == errno.ECONNRESET:
                return "connection_reset"
            if cause.errno == errno.ECONNREFUSED:
                return "connection_refused"
            if cause.errno in {errno.ENETUNREACH, errno.EHOSTUNREACH}:
                return "network_unreachable"
        if isinstance(cause, httpx.ProxyError):
            return "proxy"
        if isinstance(cause, httpx.ConnectTimeout):
            return "connect_timeout"
        if isinstance(cause, httpx.ReadTimeout):
            return "read_timeout"
        if isinstance(cause, httpx.PoolTimeout):
            return "pool_timeout"
    return "unclassified"
