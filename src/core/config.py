from dataclasses import dataclass
from pathlib import Path
import os

import yaml
from dotenv import load_dotenv


@dataclass
class RetryCfg:
    """
    Configuration section that defines retry behavior for HTTP requests.

    Attributes:
        attempts: Number of retry attempts before giving up.
        delay_ms: Initial delay between retries, in milliseconds.
        backoff_multiplier: Multiplier applied to delay on each retry
            (exponential backoff).
        retry_on_status: HTTP status codes that should trigger a retry.
    """
    attempts: int
    delay_ms: int
    backoff_multiplier: float
    retry_on_status: list[int]


@dataclass
class AppCfg:
    """
    Top-level application configuration loaded from config.yaml and
    optionally overridden by .env.

    Attributes:
        base_url: Base URL for all HTTP requests.
        timeout: Default timeout (seconds) for requests unless explicitly
            overridden.
        verify_ssl: Whether to verify SSL certificates for HTTPS requests.
        default_headers: Global default headers applied to each HTTP request.
        retry: Retry configuration (RetryCfg).
        allure_dir: Directory where Allure reports should be stored.
    """
    base_url: str
    timeout: int
    verify_ssl: bool
    default_headers: dict
    retry: RetryCfg
    allure_dir: str


def load_config() -> AppCfg:
    """
    Loads configuration from config/config.yaml and overrides values with
    .env variables if present.

    Returns:
        AppCfg: Fully resolved configuration object.
    """
    load_dotenv()

    config_path = Path("config/config.yaml")
    with config_path.open("r", encoding="utf-8") as f:
        y = yaml.safe_load(f)

    base_url = os.getenv("BASE_URL", y["base_url"])
    timeout = int(os.getenv("TIMEOUT", y["request"]["timeout"]))
    verify_ssl = (
        os.getenv("VERIFY_SSL", str(y["request"]["verify_ssl"]))
    ).lower() == "true"
    allure_dir = os.getenv("ALLURE_DIR", y["reporting"]["allure_dir"])

    return AppCfg(
        base_url=base_url,
        timeout=timeout,
        verify_ssl=verify_ssl,
        default_headers=y["request"]["default_headers"],
        retry=RetryCfg(**y["retry"]),
        allure_dir=allure_dir,
    )
