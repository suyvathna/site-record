"""
Step 5: build a DailyRecord from one day's MessageExtractions. Plain code, no LLM.

NOT IMPLEMENTED YET.

Contract:
    assemble_day(project_code, day, messages, extractions) -> DailyRecord

Rules:
- Group by site_date() (Phnom Penh calendar day), not UTC date.
- Merge duplicate manpower rows for the same company+trade by taking the
  latest stated count, not the sum (people repeat counts through the day).
  Keep all source_message_ids.
- Messages from role "engineer_rep" with instruction items fill
  engineer_instruction.
- Voice notes, PDFs and Word files go to `documents`, never to content fields.
- Gaps to raise (first set, refine after the real export):
    no_manpower           no manpower item all day
    delay_without_cause   a Delay/Weather candidate with no description of cause
    photos_no_caption     more than N photos with no caption
    voice_unreviewed      voice notes present (ask for a text summary)
"""

from datetime import date

from .models import Message
from .schema import DailyRecord, MessageExtraction


def assemble_day(
    project_code: str,
    day: date,
    messages: list[Message],
    extractions: list[MessageExtraction],
) -> DailyRecord:
    raise NotImplementedError("assemble step not built yet; see module docstring")
