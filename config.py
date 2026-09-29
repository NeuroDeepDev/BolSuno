"""Simple local configuration for Voice ↔ Text."""

WHISPER_MODEL_SIZE = "base"
MICROPHONE_DEVICE = None  # None selects the system default input device.

TTS_RATE = 1.0  # Browser speech rate multiplier; range: 0.5 to 2.0.
TTS_VOLUME = 1.0  # Browser speech volume; range: 0.0 to 1.0.