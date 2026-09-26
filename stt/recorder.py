"""Temporary in-memory microphone recording using sounddevice."""

import threading

import numpy as np


SAMPLE_RATE = 16000


def _audio_backend():
    try:
        import sounddevice as sd
    except (ImportError, OSError) as exc:
        raise RuntimeError(f"Audio input is unavailable: {exc}") from exc
    return sd


def microphone_name(device=None):
    """Return the selected input device name or raise its audio error."""
    sd = _audio_backend()
    info = sd.query_devices(device, "input")
    if info["max_input_channels"] < 1:
        raise RuntimeError("The selected audio device has no microphone input.")
    return info["name"]


class AudioRecorder:
    """Collect mono float audio chunks until stop() is called."""

    def __init__(self):
        self._stream = None
        self._chunks = []
        self._lock = threading.Lock()
        self._failure = None

    @property
    def is_recording(self):
        return self._stream is not None

    @property
    def failure(self):
        with self._lock:
            return self._failure

    def start(self, device=None):
        if self.is_recording:
            return
        sd = _audio_backend()

        with self._lock:
            self._chunks = []
            self._failure = None

        def capture(indata, frames, timing, status):
            if status:
                with self._lock:
                    self._failure = str(status)
            with self._lock:
                self._chunks.append(indata.copy())

        stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            device=device,
            channels=1,
            dtype="float32",
            callback=capture,
        )
        try:
            stream.start()
        except Exception:
            stream.close()
            raise
        self._stream = stream

    def stop(self):
        stream = self._stream
        if stream is None:
            return np.empty(0, dtype=np.float32)

        self._stream = None
        stream_error = None
        try:
            stream.stop()
        except Exception as exc:
            stream_error = exc
        finally:
            try:
                stream.close()
            except Exception as exc:
                stream_error = stream_error or exc

        with self._lock:
            chunks = self._chunks
            self._chunks = []
            failure = self._failure
        if stream_error:
            raise RuntimeError(f"Could not stop the microphone: {stream_error}") from stream_error
        if failure:
            raise RuntimeError(f"Microphone capture reported an audio error: {failure}")
        if not chunks:
            return np.empty(0, dtype=np.float32)
        return np.concatenate(chunks, axis=0).reshape(-1).astype(np.float32, copy=False)