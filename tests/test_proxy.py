"""Unit tests for speech_recognition.proxy utilities."""

from __future__ import annotations

import os
import unittest
from unittest.mock import MagicMock, patch
from urllib.request import OpenerDirector, Request

from speech_recognition.exceptions import SetupError
from speech_recognition.proxy import (
    build_boto3_proxy_config,
    build_httpx_client,
    build_requests_proxies,
    build_urllib_opener,
    grpc_proxy_env,
    urlopen_with_proxy,
)


class TestBuildUrllibOpener(unittest.TestCase):
    def test_none_returns_none(self):
        self.assertIsNone(build_urllib_opener(None))

    def test_empty_string_returns_opener(self):
        opener = build_urllib_opener("")
        self.assertIsInstance(opener, OpenerDirector)

    def test_http_proxy_returns_opener(self):
        opener = build_urllib_opener("http://proxy.example.com:8080")
        self.assertIsInstance(opener, OpenerDirector)

    def test_socks_proxy_without_pysocks_raises_setup_error(self):
        with patch.dict("sys.modules", {"sockshandler": None}):
            with self.assertRaises((SetupError, ImportError)):
                build_urllib_opener("socks5://proxy.example.com:1080")

    def test_socks_proxy_with_pysocks(self):
        mock_handler = MagicMock()
        mock_socks = MagicMock()
        mock_socks.SOCKS5 = 2
        mock_socks.SOCKS4 = 1
        mock_sockshandler = MagicMock()
        mock_sockshandler.SocksiPyHandler = mock_handler

        with patch.dict(
            "sys.modules",
            {"socks": mock_socks, "sockshandler": mock_sockshandler},
        ):
            opener = build_urllib_opener("socks5://proxy.example.com:1080")
            self.assertIsNotNone(opener)
            mock_handler.assert_called_once_with(
                2, "proxy.example.com", 1080, username=None, password=None
            )


class TestUrlopenWithProxy(unittest.TestCase):
    @patch("speech_recognition.proxy.urlopen")
    def test_none_proxy_uses_default_urlopen(self, mock_urlopen):
        req = Request("http://example.com")
        urlopen_with_proxy(req, timeout=10, proxy_url=None)
        mock_urlopen.assert_called_once_with(req, timeout=10)

    @patch("speech_recognition.proxy.urlopen")
    def test_none_timeout(self, mock_urlopen):
        req = Request("http://example.com")
        urlopen_with_proxy(req, timeout=None, proxy_url=None)
        mock_urlopen.assert_called_once_with(req)

    def test_http_proxy_uses_opener(self):
        req = Request("http://example.com")
        with patch("speech_recognition.proxy.build_urllib_opener") as mock_build:
            mock_opener = MagicMock()
            mock_build.return_value = mock_opener
            urlopen_with_proxy(
                req, timeout=5, proxy_url="http://proxy:8080"
            )
            mock_opener.open.assert_called_once_with(req, timeout=5)


class TestBuildHttpxClient(unittest.TestCase):
    def test_none_returns_none(self):
        self.assertIsNone(build_httpx_client(None))

    def test_empty_string_creates_client_no_proxy(self):
        mock_httpx = MagicMock()
        with patch.dict("sys.modules", {"httpx": mock_httpx}):
            result = build_httpx_client("")
            mock_httpx.Client.assert_called_once_with(proxy=None)
            self.assertEqual(result, mock_httpx.Client.return_value)

    def test_proxy_url_creates_client(self):
        mock_httpx = MagicMock()
        with patch.dict("sys.modules", {"httpx": mock_httpx}):
            result = build_httpx_client("http://proxy:8080")
            mock_httpx.Client.assert_called_once_with(
                proxy="http://proxy:8080"
            )
            self.assertEqual(result, mock_httpx.Client.return_value)


class TestBuildRequestsProxies(unittest.TestCase):
    def test_none_returns_none(self):
        self.assertIsNone(build_requests_proxies(None))

    def test_empty_string_disables_proxies(self):
        result = build_requests_proxies("")
        self.assertEqual(result, {"http": None, "https": None})

    def test_proxy_url(self):
        result = build_requests_proxies("http://proxy:8080")
        self.assertEqual(
            result,
            {"http": "http://proxy:8080", "https": "http://proxy:8080"},
        )


class TestBuildBoto3ProxyConfig(unittest.TestCase):
    def test_none_returns_none(self):
        self.assertIsNone(build_boto3_proxy_config(None))

    def test_empty_string(self):
        mock_config_cls = MagicMock()
        mock_botocore_config = MagicMock()
        mock_botocore_config.Config = mock_config_cls

        with patch.dict(
            "sys.modules",
            {
                "botocore": MagicMock(),
                "botocore.config": mock_botocore_config,
            },
        ):
            result = build_boto3_proxy_config("")
            mock_config_cls.assert_called_once_with(proxies={})

    def test_proxy_url(self):
        mock_config_cls = MagicMock()
        mock_botocore_config = MagicMock()
        mock_botocore_config.Config = mock_config_cls

        with patch.dict(
            "sys.modules",
            {
                "botocore": MagicMock(),
                "botocore.config": mock_botocore_config,
            },
        ):
            result = build_boto3_proxy_config("http://proxy:8080")
            mock_config_cls.assert_called_once_with(
                proxies={
                    "http": "http://proxy:8080",
                    "https": "http://proxy:8080",
                }
            )


class TestGrpcProxyEnv(unittest.TestCase):
    def test_none_is_noop(self):
        original = os.environ.get("http_proxy")
        with grpc_proxy_env(None):
            self.assertEqual(os.environ.get("http_proxy"), original)
        self.assertEqual(os.environ.get("http_proxy"), original)

    def test_sets_and_restores_env(self):
        original_http = os.environ.get("http_proxy")
        original_https = os.environ.get("https_proxy")

        with grpc_proxy_env("http://proxy:8080"):
            self.assertEqual(os.environ["http_proxy"], "http://proxy:8080")
            self.assertEqual(os.environ["https_proxy"], "http://proxy:8080")
            self.assertEqual(os.environ["HTTP_PROXY"], "http://proxy:8080")
            self.assertEqual(os.environ["HTTPS_PROXY"], "http://proxy:8080")

        # Should be restored
        self.assertEqual(os.environ.get("http_proxy"), original_http)
        self.assertEqual(os.environ.get("https_proxy"), original_https)

    def test_empty_string_clears_env(self):
        os.environ["http_proxy"] = "old_value"
        try:
            with grpc_proxy_env(""):
                self.assertNotIn("http_proxy", os.environ)
            # Restored after context
            self.assertEqual(os.environ["http_proxy"], "old_value")
        finally:
            os.environ.pop("http_proxy", None)

    def test_restores_on_exception(self):
        original = os.environ.get("http_proxy")

        class TestError(Exception):
            pass

        with self.assertRaises(TestError):
            with grpc_proxy_env("http://proxy:8080"):
                raise TestError("boom")

        self.assertEqual(os.environ.get("http_proxy"), original)


class TestRecognizerProxyUrl(unittest.TestCase):
    def test_recognizer_has_proxy_url_attribute(self):
        import speech_recognition as sr

        r = sr.Recognizer()
        self.assertIsNone(r.proxy_url)

    def test_proxy_url_is_settable(self):
        import speech_recognition as sr

        r = sr.Recognizer()
        r.proxy_url = "http://proxy:8080"
        self.assertEqual(r.proxy_url, "http://proxy:8080")


if __name__ == "__main__":
    unittest.main()
