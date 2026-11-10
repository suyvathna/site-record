# 0003 Real client data never goes through the Gemini free tier

Date: 2026-11-10. Status: accepted.

Google's pricing page (checked 2026-11-10) says free-tier content is used to improve its products; paid-tier content is not. A contractor's site group is their data, not ours to hand over.

Decision: the free tier is used only on synthetic messages (like `tests/fixtures`). Any real export goes through a paid-tier key. Estimated cost at 2.5 Flash prices ($0.30 / 1M input, $2.50 / 1M output): roughly $0.10 per active project per day. That estimate is a guess based on about 150 messages and 30 photos a day.
