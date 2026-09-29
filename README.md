# Voice ↔ Text

A lightweight utility for speaking instead of typing and listening to text instead of reading. Speech recognition runs locally with Whisper, and text-to-speech uses the browser's speech synthesis voices.

## Features

- Record from the default microphone, then transcribe locally.
- Edit, copy, or clear the transcription; reuse the text in the speech panel.
- Read typed or pasted text aloud, with a responsive Stop control.
- Configure the Whisper model and microphone device in `config.py`; choose the browser voice, rate, and volume in the speech panel.
- No accounts, database, analytics, chat, or permanent audio/transcript history.

## Technologies

- Python 3.11 (recommended; Python 3.10-3.12 are the supported target range)
- Streamlit for the local dashboard
- `sounddevice` and NumPy for temporary microphone capture
- `faster-whisper` with CTranslate2 for on-device transcription
- Browser SpeechSynthesis API for text-to-speech playback on the user's device

## System requirements

- Windows 10/11, macOS, or Linux; a microphone, speakers/headphones, and a browser with SpeechSynthesis support.
- A working local audio input/output device and permission to access it.
- About 1 GB of free disk space for the default Whisper `base` model and Python packages; larger models need more space and memory.
- Internet is needed to install packages and download the model the first time. Recognition runs locally after the model is downloaded; some browser speech voices may also require internet access.

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

Text-to-speech runs in the browser through its SpeechSynthesis API, so audio plays on the device where the dashboard is open. Select an available browser voice and adjust rate and volume in the speech panel. Available voices depend on the browser and operating system; install or enable voices in your device's speech settings if needed.

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

Enter or paste text, select a browser voice if desired, then click **Speak**. **Stop** cancels the current utterance. Playback is handled by the browser on the device using the dashboard; some browser voices may use an online service.

## Privacy

Microphone recordings are held temporarily in memory for transcription; the app does not save recordings or transcripts. Transcription text stays in the current Streamlit session unless you copy it. Speech-panel text is held in per-tab browser session storage to survive app rerenders and is not sent to the Streamlit server. The browser's selected speech service may be local or online. The app has no history, database, account, analytics, or cloud sync. Do not expose the Streamlit server to a network if other users should not access the session.

## Troubleshooting

- **Microphone unavailable or permission denied:** connect a microphone, allow desktop/browser audio access if prompted, and check the operating system's microphone privacy settings. Set `MICROPHONE_DEVICE` in `config.py` to a sounddevice input device index if the default is wrong. To list devices: `python -c "import sounddevice as sd; print(sd.query_devices())"`.
- **Audio device unavailable:** close other software holding the device, verify the OS input/output selection, then restart the app. On Linux, install the system PortAudio package if `sounddevice` cannot find PortAudio (Debian/Ubuntu: `sudo apt install libportaudio2`).
- **Model unavailable or loading failed:** confirm the model name, internet access for the initial download, and free disk space; retry the pre-download command above. Once downloaded, the model can be used offline.
- **No speech detected / empty recording:** record for a few seconds with the microphone selected and unmuted, then try again in a quieter room.
- **No speech or voices listed:** use a browser that supports SpeechSynthesis and check the device's output volume and installed speech voices. Some browsers load their voice list after the page opens.
- **Installation errors:** use 64-bit Python 3.11 and activate the virtual environment before installing requirements. CTranslate2 and audio wheels may lag the newest Python release.

## Future improvements

- Optional microphone selector populated from locally installed devices.
- Keyboard shortcuts and configurable hotkeys.
- Additional local speech engines and model-selection controls.

These are intentionally not included in the initial version.