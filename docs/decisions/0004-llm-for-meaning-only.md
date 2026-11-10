# 0004 The LLM interprets meaning only

Date: 2026-11-10. Status: accepted.

Same split as the thesis pipeline, where geometry extraction was deterministic and the LLM only did semantic association.

Decision: Khmer digit conversion, timezone grouping, role mapping, file hashing and Excel parsing are plain Python. The LLM gets a cleaned message and returns a validated `MessageExtraction`. It never writes a DailyRecord, never invents numbers, and its FIDIC event types stay candidates until a person confirms them.
