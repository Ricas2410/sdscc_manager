"""Payroll utilities for permission checks."""

from __future__ import annotations

from typing import Any

from core.models import SiteSettings


def auditor_can_view_payroll(user: Any) -> bool:
    """Return True if the user is an auditor allowed to view payroll data."""
    if not getattr(user, "is_authenticated", False):
        return False
    if not getattr(user, "is_auditor", False):
        return False
    try:
        settings_obj = SiteSettings.get_settings()
    except Exception:
        return False
    return bool(getattr(settings_obj, "allow_auditor_payroll_access", False))
