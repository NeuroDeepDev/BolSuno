"""Offline text-to-speech using locally installed system voices."""

import threading


class Speaker:
    """Run pyttsx3 on a worker thread and stop it cooperatively."""

    def __init__(self):
        self._lock = threading.Lock()
        self._thread = None
        self._stop_event = None
        self._speaking = False
        self._error = None

    @property
    def is_speaking(self):
        with self._lock:
            return self._speaking

    @property
    def error(self):
        with self._lock:
            return self._error

    def speak(self, text, voice=None, rate=180, volume=1.0):
        if not text or not text.strip():
            raise ValueError("Enter some text before clicking Speak.")

        with self._lock:
            if self._speaking:
                raise RuntimeError("Speech is already playing.")
            stop_event = threading.Event()
            self._stop_event = stop_event
            self._error = None
            self._speaking = True
            self._thread = threading.Thread(
                target=self._run,
                args=(text, voice, rate, volume, stop_event),
                daemon=True,
            )
            self._thread.start()

    def stop(self):
        with self._lock:
            stop_event = self._stop_event
        if stop_event:
            stop_event.set()

    def _run(self, text, voice, rate, volume, stop_event):
        engine = None
        loop_started = False
        try:
            import pyttsx3

            engine = pyttsx3.init()
            engine.setProperty("rate", int(rate))
            engine.setProperty("volume", max(0.0, min(1.0, float(volume))))
            if voice:
                voice_query = str(voice).casefold()
                voices = engine.getProperty("voices") or []
                selected = next(
                    (item for item in voices if item.id == voice or voice_query in item.name.casefold()),
                    None,
                )
                if selected is None:
                    raise ValueError(f"The configured TTS voice was not found: {voice}")
                engine.setProperty("voice", selected.id)

            engine.say(text)
            engine.startLoop(False)
            loop_started = True
            while engine.isBusy() and not stop_event.is_set():
                engine.iterate()
                stop_event.wait(0.01)
        except Exception as exc:
            with self._lock:
                self._error = str(exc)
        finally:
            if engine is not None:
                try:
                    engine.stop()
                except Exception:
                    pass
                if loop_started:
                    try:
                        engine.endLoop()
                    except Exception:
                        pass
            with self._lock:
                self._speaking = False
                self._stop_event = None