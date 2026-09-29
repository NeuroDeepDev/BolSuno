"""Voice ↔ Text: a local speech transcription and speech synthesis utility."""

import streamlit as st
from faster_whisper import WhisperModel

import config
from stt.recorder import AudioRecorder, microphone_name
from stt.transcriber import NoSpeechDetected, transcribe_audio
from ui.components import browser_speech_component, copy_button, status_badge


st.set_page_config(page_title="Voice ↔ Text", page_icon="🎙️", layout="wide")

st.markdown(
    """
    <style>
    .stApp { background: #101614; color: #e6eeeb; }
    html, body, [class*="css"] { font-family: "Segoe UI", "Aptos", sans-serif; }
    [data-testid="stHeader"] { background: rgba(16, 22, 20, 0.92); }
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: linear-gradient(145deg, rgba(29, 40, 36, .96), rgba(22, 31, 28, .96));
        border: 1px solid #33443e; border-radius: 10px; padding: 1.25rem 1.4rem;
    }
    h1 { color: #f0f5f3; font-weight: 600; letter-spacing: 0; }
    h2, h3 { color: #e4ece8; letter-spacing: 0; }
    p, label, .stCaption { color: #aebdb7 !important; }
    [data-testid="stTextArea"] textarea {
        background: #101815; color: #eef4f1; border: 1px solid #3c4f48;
        border-radius: 7px; line-height: 1.55;
    }
    [data-testid="stTextArea"] textarea:focus { border-color: #73c9a1; }
    .status-badge { display: inline-flex; align-items: center; gap: 8px; margin: 2px 0 12px;
        color: #bac8c2; font-size: 13px; }
    .status-badge span { width: 8px; height: 8px; border-radius: 50%; background: #77867f; }
    .status-badge.active span { background: #65dfa0; box-shadow: 0 0 0 4px rgba(101, 223, 160, .13); }
    div.stButton > button { border-radius: 7px; min-height: 42px; font-weight: 600; }
    div.stButton > button[kind="primary"] { background: #72d4a4; color: #13231b; border: 0; }
    div.stButton > button[kind="primary"]:hover { background: #8ae2b6; }
    .privacy-note { color: #8c9c95; font-size: 13px; border-top: 1px solid #2b3933;
        padding-top: 14px; margin-top: 12px; }
    @media (max-width: 700px) {
        [data-testid="stVerticalBlockBorderWrapper"] { padding: 1rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource(show_spinner=False)
def load_whisper_model(model_size):
    return WhisperModel(model_size, device="cpu", compute_type="int8")


def initialize_session():
    defaults = {
        "transcription": "",
        "speech_text": "",
        "stt_status": "Ready",
        "speech_seed": 0,
        "recorder": AudioRecorder(),
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def clear_transcription():
    st.session_state.transcription = ""
    st.session_state.stt_status = "Ready"


def render_speech_to_text():
    recorder = st.session_state.recorder
    recording = recorder.is_recording
    try:
        input_name = microphone_name(config.MICROPHONE_DEVICE)
        microphone_ready = True
    except Exception as exc:
        input_name = f"Microphone unavailable: {exc}"
        microphone_ready = False

    with st.container(border=True):
        st.subheader("🎙️  Speech to Text")
        status_badge(st.session_state.stt_status, active=recording)
        st.caption(input_name)

        start_col, stop_col = st.columns(2)
        with start_col:
            if st.button(
                "Start Speaking",
                type="primary",
                disabled=recording or not microphone_ready,
                use_container_width=True,
                key="start_recording",
            ):
                try:
                    recorder.start(config.MICROPHONE_DEVICE)
                    st.session_state.stt_status = "Listening..."
                except Exception as exc:
                    st.session_state.stt_status = f"Microphone unavailable: {exc}"
                st.rerun()
        with stop_col:
            if st.button(
                "Stop Recording",
                disabled=not recording,
                use_container_width=True,
                key="stop_recording",
            ):
                try:
                    st.session_state.stt_status = "Processing..."
                    with st.spinner("Transcribing locally..."):
                        audio = recorder.stop()
                        if len(audio) == 0:
                            raise ValueError("The recording is empty. Speak for a few seconds and try again.")
                        model = load_whisper_model(config.WHISPER_MODEL_SIZE)
                        st.session_state.transcription = transcribe_audio(audio, model)
                    st.session_state.stt_status = "Transcription complete"
                except NoSpeechDetected as exc:
                    st.session_state.stt_status = str(exc)
                except Exception as exc:
                    st.session_state.stt_status = f"Speech recognition failed: {exc}"
                st.rerun()

        st.text_area(
            "Transcription",
            key="transcription",
            height=280,
            placeholder="Your transcription will appear here. You can edit it or reuse it in Text to Speech.",
        )
        copy_col, clear_col = st.columns([1, 1])
        with copy_col:
            if st.session_state.transcription:
                copy_button(st.session_state.transcription)
        with clear_col:
            st.button(
                "Clear",
                on_click=clear_transcription,
                use_container_width=True,
                key="clear_transcription",
            )
        if st.session_state.transcription:
            if st.button("Use in Text to Speech", use_container_width=False):
                st.session_state.speech_text = st.session_state.transcription
                st.session_state.speech_seed += 1


def render_text_to_speech():
    with st.container(border=True):
        st.subheader("🔊  Text to Speech")
        browser_speech_component(
            initial_text=st.session_state.speech_text,
            seed=st.session_state.speech_seed,
            rate=config.TTS_RATE,
            volume=config.TTS_VOLUME,
        )


initialize_session()
st.title("Voice ↔ Text")
st.caption("Dictate text or hear it read aloud.")

left, right = st.columns(2, gap="large")
with left:
    render_speech_to_text()
with right:
    render_text_to_speech()

st.markdown(
    '<div class="privacy-note">Audio is held temporarily for transcription. Text-to-speech uses the selected browser voice, '
    'which may be local or online. No recordings, transcripts, or speech history are saved by the app.</div>',
    unsafe_allow_html=True,
)