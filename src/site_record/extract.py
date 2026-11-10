"""
Step 4: the only step that calls an LLM.

NOT IMPLEMENTED YET. Next build step after the first real export has been
ingested and looked at (see CLAUDE.md, "Next steps").

Contract:
    extract_message(msg, role, prompt_version) -> MessageExtraction

Design rules (decisions 0003 and 0004):
- Input is the normalised message (Khmer digits already ASCII) plus the
  sender's role from config. For photos, the image is sent with its caption.
- Output must validate against schema.MessageExtraction. Use Gemini
  structured output with the Pydantic model; on validation failure, retry
  once, then store the message as unextracted rather than guessing.
- The prompt lives in prompts/extract_vN.md, never inline in code. The
  prompt version is saved with every extraction so results are reproducible.
- Never estimate quantities or progress % from an image.
- Real client data only through the paid tier (free-tier content is used
  by Google to improve products).

Open item: check whether Gemini structured output accepts the discriminated
union in MessageExtraction.items. If it doesn't, flatten to one Item model
with `section` plus optional fields, and convert to the typed items in code.
"""

from .models import Message
from .schema import MessageExtraction


def extract_message(msg: Message, role: str | None, prompt_version: str = "v1") -> MessageExtraction:
    raise NotImplementedError("extract step not built yet; see module docstring")
