"""Centralized proxy utilities for SpeechRecognition.

Provides helper functions that build proxy-aware clients for each HTTP
library used in the project (urllib, httpx, requests, boto3, gRPC).

Proxy URL semantics:
    None  - use system/env proxy settings (default, backward compatible)
    ""    - explicitly disable proxies
    "http://host:port"  - use that HTTP proxy
    "socks5://host:port" - SOCKS proxy (requires PySocks)
"""

from __future__ import annotations

import contextlib
import os
from urllib.request import (
    OpenerDirector,
    ProxyHandler,
    Request,
    build_opener,
    urlopen,
)

from speech_recognition.exceptions import SetupError


def build_urllib_opener(proxy_url: str | None) -> OpenerDirector | None:
    """Return an ``OpenerDirector`` configured with *proxy_url*.

    Returns ``None`` when *proxy_url* is ``None`` (use default behaviour).
    An empty string disables proxying; a ``socks5://`` URL requires
    ``PySocks`` + ``sockshandler``.
    """
    if proxy_url is None:
        return None

    if proxy_url == "":
        return build_opener(ProxyHandler({}))

    if proxy_url.startswith("socks"):
        try:
            from sockshandler import SocksiPyHandler
        except ImportError:
            raise SetupError(
                "SOCKS proxy support requires the PySocks package. "
                "Install it with: pip install PySocks"
            )

        from urllib.parse import urlparse

        parsed = urlparse(proxy_url)
        import socks

        socks_type_map = {
            "socks4": socks.SOCKS4,
            "socks5": socks.SOCKS5,
            "socks5h": socks.SOCKS5,
        }
        socks_type = socks_type_map.get(parsed.scheme)
        if socks_type is None:
            raise SetupError(
                f"Unsupported SOCKS scheme: {parsed.scheme!r}. "
                "Use socks4, socks5, or socks5h."
            )

        return build_opener(
            SocksiPyHandler(
                socks_type,
                parsed.hostname,
                parsed.port or 1080,
                username=parsed.username,
                password=parsed.password,
            )
        )

    # HTTP/HTTPS proxy
    return build_opener(
        ProxyHandler({"http": proxy_url, "https": proxy_url})
    )


def urlopen_with_proxy(request: Request, timeout: int | None, proxy_url: str | None):
    """Drop-in replacement for ``urlopen()`` that respects *proxy_url*."""
    opener = build_urllib_opener(proxy_url)
    kwargs = {}
    if timeout is not None:
        kwargs["timeout"] = timeout

    if opener is not None:
        return opener.open(request, **kwargs)
    return urlopen(request, **kwargs)


def build_httpx_client(proxy_url: str | None):
    """Return an ``httpx.Client`` configured with *proxy_url*.

    Returns ``None`` when *proxy_url* is ``None`` (caller should use
    the SDK default client).
    """
    if proxy_url is None:
        return None

    import httpx

    if proxy_url == "":
        return httpx.Client(proxy=None)

    return httpx.Client(proxy=proxy_url)


def build_requests_proxies(proxy_url: str | None) -> dict | None:
    """Return a *proxies* dict suitable for ``requests.get/post(proxies=...)``.

    Returns ``None`` when *proxy_url* is ``None`` (use default behaviour).
    """
    if proxy_url is None:
        return None

    if proxy_url == "":
        return {"http": None, "https": None}

    return {"http": proxy_url, "https": proxy_url}


def build_boto3_proxy_config(proxy_url: str | None):
    """Return a ``botocore.config.Config`` with proxy settings.

    Returns ``None`` when *proxy_url* is ``None`` (use default behaviour).
    """
    if proxy_url is None:
        return None

    from botocore.config import Config

    if proxy_url == "":
        return Config(proxies={})

    return Config(proxies={"http": proxy_url, "https": proxy_url})


@contextlib.contextmanager
def grpc_proxy_env(proxy_url: str | None):
    """Context manager that temporarily sets gRPC-compatible env vars.

    gRPC reads ``http_proxy`` / ``https_proxy`` from the environment.
    This sets them for the duration of the ``with`` block, then restores
    the previous values.

    .. warning:: This is NOT thread-safe.
    """
    if proxy_url is None:
        yield
        return

    env_keys = ("http_proxy", "https_proxy",
                "HTTP_PROXY", "HTTPS_PROXY")
    saved = {k: os.environ.get(k) for k in env_keys}

    try:
        if proxy_url == "":
            for k in env_keys:
                os.environ.pop(k, None)
        else:
            for k in env_keys:
                os.environ[k] = proxy_url
        yield
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
