"""
Enums copied from CEIP (suyvathna/CEIP, backend/app/constants/) so the
output of this repo can be posted into CEIP later without a translation layer.

Copied, not imported: this repo must run without CEIP's stack
(Postgres, MinIO, FastAPI). If CEIP changes these values, update here too.
Source commit at copy time: 1230a6e.
"""

from enum import Enum


class EventType(str, Enum):
    # Operational
    PROGRESS = "Progress"
    DELAY = "Delay"
    WEATHER = "Weather"
    QUALITY = "Quality"
    SAFETY = "Safety"
    RFI = "RFI"
    INSTRUCTION = "Instruction"
    INSPECTION = "Inspection"
    DELIVERY = "Delivery"
    INCIDENT = "Incident"
    ACCESS_RESTRICTION = "Access Restriction"
    OTHER = "Other"
    # FIDIC Red Book 2017 delay/claim grounds
    ADVERSE_WEATHER = "Adverse Weather"
    DESIGN_CHANGE_VARIATION = "Design Change / Variation Order"
    DELAYED_DRAWINGS_OR_INSTRUCTIONS = "Delayed Drawings or Instructions"
    LATE_ACCESS_TO_SITE = "Late Access to Site"
    ERRORS_IN_SETTING_OUT = "Errors in Setting-Out Data"
    UNFORESEEABLE_PHYSICAL_CONDITIONS = "Unforeseeable Physical Conditions"
    FOSSILS_ANTIQUITIES = "Fossils / Antiquities"
    ADDITIONAL_TESTING = "Employer-Instructed Additional Testing"
    DELAY_BY_AUTHORITIES = "Delay Caused by Authorities"
    EMPLOYER_SUSPENSION = "Employer's Suspension of Work"
    INTERFERENCE_WITH_TESTS_ON_COMPLETION = "Interference with Tests on Completion"
    CHANGE_IN_LAWS = "Change in Laws"
    EXCEPTIONAL_EVENT = "Exceptional Event (Force Majeure)"
    EPIDEMIC_OR_GOVERNMENT_ACTION_SHORTAGE = "Epidemic / Government Action Shortage"
    CONTRACTOR_SUSPENSION_FOR_NONPAYMENT = "Contractor's Suspension for Non-Payment"
    LATE_PAYMENT_BY_EMPLOYER = "Late Payment by Employer"
    EMPLOYER_DELAY_GENERAL = "Employer-Caused Delay (General)"


class PhotoCategory(str, Enum):
    GENERAL = "General"
    MANPOWER = "Manpower"
    EQUIPMENT = "Equipment"
    DELIVERY = "Delivery"
    INSPECTION = "Inspection"
    HSE = "HSE"
    WEATHER = "Weather"
    VISITOR = "Visitor"
