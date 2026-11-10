"""
Deterministic clean-up before any LLM sees a message.

Anything that can be done with plain code is done here, so the LLM is only
asked to interpret meaning (decision 0004). Same split as the thesis:
geometry was deterministic, the LLM only did semantic association.
"""

from datetime import date, datetime
from zoneinfo import ZoneInfo

# Khmer digits ០-៩ (U+17E0..U+17E9) to ASCII. Also the Khmer "lek attak"
# digits U+17F0..U+17F9 are divination numerals, not used on site; ignored.
_KHMER_DIGITS = str.maketrans("០១២៣៤៥៦៧៨៩", "0123456789")


def khmer_digits_to_ascii(text: str) -> str:
    """'កម្មករ ១២ នាក់' -> 'កម្មករ 12 នាក់'. Leaves everything else untouched."""
    return text.translate(_KHMER_DIGITS)


def normalize_text(text: str) -> str:
    """Apply all text normalisation steps in a fixed order."""
    text = khmer_digits_to_ascii(text)
    # Zero-width spaces are common in Khmer text (used as word break hints).
    # Keep them: removing them can merge words. Only strip outer whitespace.
    return text.strip()


def site_date(sent_at_utc: datetime, tz: str = "Asia/Phnom_Penh") -> date:
    """
    The calendar day on site a message belongs to.

    A message sent at 23:30 UTC belongs to the NEXT day in Phnom Penh (UTC+7).
    Grouping by UTC date would put night-shift messages in the wrong diary.
    """
    if sent_at_utc.tzinfo is None:
        raise ValueError("sent_at_utc must be timezone-aware")
    return sent_at_utc.astimezone(ZoneInfo(tz)).date()


def role_for(sender_id: str | None, roles: dict[str, str]) -> str | None:
    """Map a Telegram sender id to a site role from the project config."""
    if sender_id is None:
        return None
    return roles.get(sender_id)
