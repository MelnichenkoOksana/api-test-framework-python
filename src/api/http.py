import json

import requests

from src.core.allure_utils import attach_text
from src.core.config import load_config
from src.core.logger import get_logger
from src.core.retry import retry

cfg = load_config()
log = get_logger("http")


class HttpClient:
    """
    Thin wrapper around requests.Session with built-in retry support,
    configuration-based defaults, and automatic Allure attachments.

    Attributes:
        base_url: Base URL for all outgoing HTTP requests.
        session: A persistent requests.Session with preconfigured headers.
    """

    def __init__(self, base_url: str = cfg.base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update(cfg.default_headers)

    @retry()
    def request(self, method: str, path: str, **kwargs) -> requests.Response:
        """
        Sends an HTTP request using preconfigured session and settings.
        Automatically attaches request/response details to Allure report.

        Args:
            method: HTTP method ("get", "post", "put", etc.).
            path: Endpoint path appended to base_url.
            **kwargs: Additional parameters passed to requests
                      (params, json, headers, etc.).

        Returns:
            requests.Response: Response object returned by the server.
        """
        url = self.base_url + path
        timeout = kwargs.pop("timeout", cfg.timeout)
        verify = kwargs.pop("verify", cfg.verify_ssl)

        log.debug("%s %s | kwargs=%s", method.upper(), url, kwargs)

        # --- Allure: attach request info ---
        req_info = {
            "method": method.upper(),
            "url": url,
            "timeout": timeout,
            "verify": verify,
            "params": kwargs.get("params"),
            "json": kwargs.get("json"),
            "data": kwargs.get("data"),
            "headers": kwargs.get("headers"),
        }
        attach_text("HTTP request", json.dumps(req_info, indent=2))

        resp = self.session.request(
            method=method,
            url=url,
            timeout=timeout,
            verify=verify,
            **kwargs,
        )

        log.debug("Response %s | headers=%s", resp.status_code, dict(resp.headers))

        # --- Allure: attach response info ---
        resp_info = {
            "status_code": resp.status_code,
            "headers": dict(resp.headers),
            "url": resp.url,
        }
        attach_text("HTTP response meta", json.dumps(resp_info, indent=2))
        attach_text("HTTP response body", resp.text)

        return resp
