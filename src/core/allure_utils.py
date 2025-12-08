from typing import Optional

try:
    import allure
except ImportError:
    allure = None

from src.core.logger import get_logger

log = get_logger("allure_utils")


def attach_text(
    name: str,
    content: str,
    attachment_type: Optional["allure.attachment_type"] = None
) -> None:
    """
    Safely attaches text content to Allure report.
    If Allure is not available (e.g., local run without plugin),
    the function silently returns without raising errors.

    Args:
        name: Human-readable label for the attachment.
        content: Text or JSON string that should appear in the report.
        attachment_type: Optional allure attachment type. Defaults to TEXT.
    """
    if allure is None:
        return

    if attachment_type is None:
        attachment_type = allure.attachment_type.TEXT

    try:
        allure.attach(content, name=name, attachment_type=attachment_type)
    except (ValueError, TypeError) as exc:
        # Known safe-to-ignore errors — wrong format or type mismatch
        log.warning("Failed to attach Allure attachment '%s': %s", name, exc)
    except Exception as exc:
        # Unexpected error — we report it, but do NOT break test execution
        log.error("Unexpected error during Allure attach '%s': %s", name, exc)
