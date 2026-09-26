# Voice ↔ Text

A lightweight personal desktop utility for speaking instead of typing and listening to text instead of reading. Speech recognition runs locally with Whisper, and text-to-speech uses the operating system's local voices through `pyttsx3`.

## Features

- Record from the default microphone, then transcribe locally.
- Edit, copy, or clear the transcription; reuse the text in the speech panel.
- Read typed or pasted text aloud, with a responsive Stop control.
- Configure the Whisper model, microphone device, TTS voice, rate, and volume in `config.py`.
- No accounts, database, analytics, chat, or permanent audio/transcript history.

## Technologies

- Python 3.11 (recommended; Python 3.10-3.12 are the supported target range)
- Streamlit for the local dashboard
- `sounddevice` and NumPy for temporary microphone capture
- `faster-whisper` with CTranslate2 for on-device transcription
- `pyttsx3` for offline system-voice speech synthesis

## System requirements

- Windows 10/11, macOS, or Linux; a microphone and speakers/headphones for full use.
- A working local audio input/output device and permission to access it.
- About 1 GB of free disk space for the default Whisper `base` model and Python packages; larger models need more space and memory.
- Internet is needed only to install packages and download the model the first time. After model download, recognition runs locally.

## Installation (Windows)

Install Python 3.11 from [python.org](https://www.python.org/downloads/) and enable **Add Python to PATH** during setup. In PowerShell, from this project directory:

```powershell
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Speech recognition model setup

The default model is `base` and is downloaded by `faster-whisper` on the first transcription. To download it ahead of time, with the virtual environment active, run:

```powershell
python -c "from faster_whisper import WhisperModel; WhisperModel('base', device='cpu', compute_type='int8')"
```

Model weights are kept in the normal Hugging Face cache on your computer. To change the model, edit `WHISPER_MODEL_SIZE` in `config.py` and use the same command with that model name (`tiny`, `base`, `small`, `medium`, or `large-v3`). Larger models are slower and use more memory. The first model download requires internet; inference does not.

## Text-to-speech setup

`pyttsx3` uses voices already installed on the computer and does not download voice data. On Windows it uses SAPI5 voices; install or enable an additional Windows speech voice in system settings if desired. On Linux, install the system `espeak-ng` package if no voice is available (for Debian/Ubuntu: `sudo apt install espeak-ng`). macOS uses its built-in speech voices.

To inspect installed voice identifiers for `TTS_VOICE` in `config.py`:

```powershell
python -c "import pyttsx3; e=pyttsx3.init(); print([(v.id, v.name) for v in e.getProperty('voices')])"
```

Set `TTS_VOICE` to an exact voice ID or a case-insensitive part of a voice name. Leave it as `None` to use the system default. Adjust `TTS_RATE` and `TTS_VOLUME` in `config.py` as needed.

## Run

With the virtual environment active:

```powershell
streamlit run app.py
```

Streamlit opens the local dashboard in your browser. It is a local desktop-style interface; keep the terminal running while using it.

## How it works

### Speech to Text

Click **Start Speaking** to open the selected microphone as a live audio stream. Audio chunks are held only in memory while recording. Click **Stop Recording** to close the microphone; the in-memory audio is passed to the local Whisper model, and the temporary chunks are discarded. The recognized text is placed in an editable text area. Nothing is sent to a speech or cloud API.

### Text to Speech

Enter or paste text, then click **Speak**. A background worker hands it to the installed system speech engine. **Stop** signals that worker to stop the current utterance promptly. Text is not written to disk by the app.

## Privacy

Microphone audio and entered text are processed on this computer. Recordings are kept temporarily in process memory only until recognition finishes or the app session ends; the app does not write audio, transcriptions, or speech text to files, and has no history, database, account, analytics, or cloud sync. Transcription text stays in the current Streamlit session unless you copy it yourself. The one-time Whisper model download is the only application data fetched from the internet; it contains model weights, not your recordings or text. The operating system's speech engine is local. Note that Streamlit's local server is intended for personal use on your machine; do not expose it to a network if other users should not access the session.

## Troubleshooting

- **Microphone unavailable or permission denied:** connect a microphone, allow desktop/browser audio access if prompted, and check the operating system's microphone privacy settings. Set `MICROPHONE_DEVICE` in `config.py` to a sounddevice input device index if the default is wrong. To list devices: `python -c "import sounddevice as sd; print(sd.query_devices())"`.
- **Audio device unavailable:** close other software holding the device, verify the OS input/output selection, then restart the app. On Linux, install the system PortAudio package if `sounddevice` cannot find PortAudio (Debian/Ubuntu: `sudo apt install libportaudio2`).
- **Model unavailable or loading failed:** confirm the model name, internet access for the initial download, and free disk space; retry the pre-download command above. Once downloaded, the model can be used offline.
- **No speech detected / empty recording:** record for a few seconds with the microphone selected and unmuted, then try again in a quieter room.
- **TTS engine unavailable:** verify that the OS has a speech voice installed. On Linux, install `espeak-ng`; on Windows, check Speech settings. Restart Streamlit after changing system voices.
- **Installation errors:** use 64-bit Python 3.11 and activate the virtual environment before installing requirements. CTranslate2 and audio wheels may lag the newest Python release.

## Future improvements

- Optional microphone and voice selectors populated from locally installed devices/voices.
- Keyboard shortcuts and configurable hotkeys.
- Additional local speech engines and model-selection controls.

These are intentionally not included in the initial version.