"""Local transcription with a cached faster-whisper model."""


class NoSpeechDetected(Exception):
    """Raised when the recording contains no recognized speech."""


def transcribe_audio(audio, model):
    if audio is None or len(audio) == 0:
        raise ValueError("The recording is empty.")

    segments, _ = model.transcribe(audio, beam_size=5, vad_filter=True)
    text = " ".join(segment.text.strip() for segment in segments).strip()
    if not text:
        raise NoSpeechDetected("No speech was detected. Try speaking closer to the microphone.")
    return text