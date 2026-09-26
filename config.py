"""Simple local configuration for Voice ↔ Text."""

WHISPER_MODEL_SIZE = "base"
MICROPHONE_DEVICE = None  # None selects the system default input device.

TTS_VOICE = None  # None selects the system default; otherwise use a voice ID/name.
TTS_RATE = 180
TTS_VOLUME = 1.0  # Range: 0.0 to 1.0.