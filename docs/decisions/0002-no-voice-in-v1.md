# 0002 No voice transcription in v1

Date: 2026-11-10. Status: accepted.

Khmer speech recognition is not reliable enough. ElevenLabs' published FLEURS benchmark puts Gemini 2.0 Flash at 32.8% WER and Whisper large-v3 at 100% WER for Khmer (their page also contradicts itself, so treat the figures with caution). Site speech mixes Khmer, English terms and numbers, which is harder still.

Decision: v1 reads text (Khmer or English), photos with captions and Excel. Voice notes are stored as untouched evidence, tagged unreviewed, and the evening check asks the engineer for a text summary when voice notes exist. They can be transcribed later once Khmer ASR improves.
