"""
The record schema. This file is the product: it decides what the LLM may
extract, what the daily report shows and what the delay register can prove.

Two layers:

1. `MessageExtraction` is what the LLM returns for ONE message. It is a list
   of items, each tagged with the Daily Log section it belongs to. The LLM
   never writes a DailyRecord directly.

2. `DailyRecord` is assembled by plain code from confirmed items. Its fields
   mirror CEIP's DailyLogCreate (backend/app/schemas/daily_log.py) so it can be
   posted into CEIP later. Two additions CEIP doesn't have yet:
   `source_message_ids` on every entry (traceability to the evidence store)
   and `confirmed` (the site engineer approved it).

Rules the schema enforces:
- Every extracted item points back to the message it came from.
- Numbers are only ever copied from text, never estimated from photos.
- FIDIC event types are candidates until a person confirms them.
"""

from datetime import date, time
from enum import Enum
from typing import Annotated, Literal

from pydantic import BaseModel, Field

from .ceip_enums import EventType, PhotoCategory


# ---------------------------------------------------------------------------
# Layer 1: what the LLM returns per message
# ---------------------------------------------------------------------------

class Language(str, Enum):
    KHMER = "km"
    ENGLISH = "en"
    MIXED = "mixed"
    NONE = "none"           # photo with no caption, sticker, etc.


class _Item(BaseModel):
    # Short quote of the words in the message that support this item.
    # Lets a reviewer check the extraction without reopening the chat.
    evidence_quote: str = Field(default="", max_length=300)


class WorkItem(_Item):
    section: Literal["work_completed"] = "work_completed"
    activity: str                       # e.g. "slab concrete pour"
    location: str | None = None         # e.g. "Level 3, grid A-C"
    quantity: float | None = None       # only if stated in text
    unit: str | None = None


class ManpowerItem(_Item):
    section: Literal["manpower"] = "manpower"
    company: str | None = None
    trade: str | None = None
    workers_count: int                  # only if stated in text


class EquipmentItem(_Item):
    section: Literal["equipment"] = "equipment"
    equipment_name: str
    location: str | None = None
    comments: str | None = None


class DeliveryItem(_Item):
    section: Literal["delivery"] = "delivery"
    contents: str
    delivered_from: str | None = None
    delivery_time: time | None = None


class InspectionItem(_Item):
    section: Literal["inspection"] = "inspection"
    inspection_type: str | None = None
    inspecting_entity: str | None = None
    location_area: str | None = None
    result: str | None = None


class HSEItem(_Item):
    section: Literal["hse"] = "hse"
    category: str | None = None         # toolbox talk, near miss, incident, PPE...
    description: str


class VisitorItem(_Item):
    section: Literal["visitor"] = "visitor"
    visitor_name: str | None = None
    company: str | None = None
    purpose: str | None = None


class WeatherItem(_Item):
    section: Literal["weather"] = "weather"
    start_time: time | None = None
    end_time: time | None = None
    caused_delay: bool = False
    comments: str | None = None


class InstructionItem(_Item):
    section: Literal["instruction"] = "instruction"
    instruction: str
    given_by_role: str | None = None    # filled from config roles, not guessed


class EventCandidateItem(_Item):
    section: Literal["event"] = "event"
    # A candidate only. The engineer confirms or rejects it in the evening check.
    event_type: EventType
    description: str


class PlanItem(_Item):
    section: Literal["tomorrow_plan"] = "tomorrow_plan"
    plan: str


ExtractedItem = Annotated[
    WorkItem | ManpowerItem | EquipmentItem | DeliveryItem | InspectionItem
    | HSEItem | VisitorItem | WeatherItem | InstructionItem
    | EventCandidateItem | PlanItem,
    Field(discriminator="section"),
]


class MessageExtraction(BaseModel):
    message_id: int
    language: Language
    is_site_relevant: bool              # False for greetings, jokes, "ok", stickers
    photo_category: PhotoCategory | None = None   # only for photo messages
    items: list[ExtractedItem] = []


# ---------------------------------------------------------------------------
# Layer 2: the assembled daily record (CEIP DailyLogCreate shape)
# ---------------------------------------------------------------------------

class _Entry(BaseModel):
    source_message_ids: list[int]
    confirmed: bool = False


class ManpowerEntry(_Entry):
    company: str | None = None
    trade: str | None = None
    position: str | None = None
    workers_count: int = 0
    hours: float | None = None
    comments: str | None = None


class EquipmentEntry(_Entry):
    equipment_name: str
    equipment_type: str | None = None
    hours_operating: float | None = None
    hours_idle: float | None = None
    inspected: bool = False
    inspection_time: time | None = None
    location: str | None = None
    comments: str | None = None


class DeliveryEntry(_Entry):
    delivery_time: time | None = None
    delivered_from: str | None = None
    tracking_number: str | None = None
    contents: str | None = None
    comments: str | None = None


class InspectionEntry(_Entry):
    start_time: time | None = None
    end_time: time | None = None
    inspection_type: str | None = None
    inspecting_entity: str | None = None
    inspector_name: str | None = None
    location_area: str | None = None
    comments: str | None = None


class HSEEntry(_Entry):
    entry_time: time | None = None
    category: str | None = None
    description: str | None = None
    action_taken: str | None = None
    reported_by: str | None = None


class VisitorEntry(_Entry):
    time_in: time | None = None
    time_out: time | None = None
    visitor_name: str | None = None
    company: str | None = None
    purpose: str | None = None
    host_name: str | None = None


class WeatherObservation(_Entry):
    start_time: time | None = None
    end_time: time | None = None
    caused_delay: bool = False
    comments: str | None = None


class PhotoRef(BaseModel):
    message_id: int
    path: str
    sha256: str | None = None
    category: PhotoCategory = PhotoCategory.GENERAL
    caption: str = ""


class DocumentRef(BaseModel):
    """PDFs, Word files, voice notes: stored and listed, content not read in v1."""
    message_id: int
    kind: str
    file_name: str | None = None
    path: str | None = None


class EventCandidate(_Entry):
    event_type: EventType
    description: str


class Gap(BaseModel):
    """Something the evening check should ask the site engineer about."""
    code: str                           # e.g. "no_manpower", "delay_without_cause"
    question: str


class DailyRecord(BaseModel):
    project_code: str
    diary_date: date

    # CEIP "Notes" block
    work_completed: str | None = None
    delays: str | None = None
    engineer_instruction: str | None = None
    tomorrow_plan: str | None = None
    remarks: str | None = None

    # CEIP narrative overflow
    manpower_notes: str | None = None
    equipment_notes: str | None = None
    materials_notes: str | None = None
    hse_notes: str | None = None
    visitor_notes: str | None = None

    # CEIP structured logs
    weather_observations: list[WeatherObservation] = []
    manpower_entries: list[ManpowerEntry] = []
    equipment_entries: list[EquipmentEntry] = []
    delivery_entries: list[DeliveryEntry] = []
    inspection_entries: list[InspectionEntry] = []
    hse_entries: list[HSEEntry] = []
    visitor_entries: list[VisitorEntry] = []

    # Not in CEIP's DailyLogCreate (CEIP stores these as Evidence / Events)
    photos: list[PhotoRef] = []
    documents: list[DocumentRef] = []
    event_candidates: list[EventCandidate] = []
    gaps: list[Gap] = []

    message_count: int = 0
    engineer_confirmed: bool = False
