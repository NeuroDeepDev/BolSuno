"""Small UI helpers shared by the Streamlit dashboard."""

import json

import streamlit as st
import streamlit.components.v1 as components


def status_badge(label, active=False):
    state_class = "active" if active else "idle"
    st.markdown(
        f'<div class="status-badge {state_class}"><span></span>{label}</div>',
        unsafe_allow_html=True,
    )


def copy_button(text):
    safe_text = json.dumps(text).replace("</", "<\\/")
    components.html(
        f"""<button id="copy" type="button">Copy Text</button>
<span id="result" role="status"></span>
<style>
body {{ margin: 0; font-family: sans-serif; background: transparent; color: #dce6e5; }}
button {{ border: 1px solid #38504d; border-radius: 7px; padding: 9px 14px;
  background: #182421; color: #e5efed; font-size: 14px; cursor: pointer; }}
button:hover {{ background: #21332f; }}
#result {{ margin-left: 10px; font-size: 13px; color: #78d2a7; }}
</style>
<script>
const value = {safe_text};
document.getElementById('copy').addEventListener('click', async () => {{
  const result = document.getElementById('result');
  try {{
    await navigator.clipboard.writeText(value);
    result.textContent = 'Copied';
  }} catch (_) {{
    const field = document.createElement('textarea');
    field.value = value;
    document.body.appendChild(field);
    field.select();
    const copied = document.execCommand('copy');
    field.remove();
    result.textContent = copied ? 'Copied' : 'Copy unavailable';
  }}
}});
</script>""",
        height=48,
        scrolling=False,
    )


def browser_speech_component(initial_text="", seed=0, rate=1.0, volume=1.0):
    safe_text = json.dumps(initial_text or "").replace("</", "<\\/")
    safe_seed = json.dumps(str(seed))
    initial_rate = max(0.5, min(2.0, float(rate)))
    initial_volume = max(0.0, min(1.0, float(volume)))
    html = """
<div id="panel">
  <label for="text">Text to read aloud</label>
  <textarea id="text" placeholder="Type or paste text here, then click Speak."></textarea>
  <div class="settings">
    <label>Voice<select id="voice"><option value="">System default</option></select></label>
    <label>Rate <output id="rate-value"></output>
      <input id="rate" type="range" min="0.5" max="2" step="0.1" value="__RATE__">
    </label>
    <label>Volume <output id="volume-value"></output>
      <input id="volume" type="range" min="0" max="1" step="0.05" value="__VOLUME__">
    </label>
  </div>
  <div class="actions">
    <button id="speak" class="primary" type="button">Speak</button>
    <button id="stop" type="button" disabled>Stop</button>
    <button id="clear" type="button">Clear</button>
    <span id="status" role="status" aria-live="polite"></span>
  </div>
</div>
<style>
  * { box-sizing: border-box; }
  body { margin: 0; color: #e6eeeb; font-family: "Segoe UI", "Aptos", sans-serif; }
  #panel { display: grid; gap: 12px; }
  label { display: grid; gap: 6px; color: #bac8c2; font-size: 13px; }
  textarea, select {
    width: 100%; border: 1px solid #3c4f48; border-radius: 7px;
    background: #101815; color: #eef4f1; font: inherit;
  }
  textarea { min-height: 175px; padding: 10px 12px; line-height: 1.55; resize: vertical; }
  textarea:focus, select:focus { outline: 1px solid #73c9a1; border-color: #73c9a1; }
  select { min-height: 38px; padding: 6px 8px; }
  .settings { display: grid; grid-template-columns: minmax(150px, 1.5fr) 1fr 1fr; gap: 12px; }
  output { color: #e6eeeb; }
  input[type="range"] { width: 100%; accent-color: #72d4a4; }
  .actions { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
  button {
    min-height: 40px; padding: 0 14px; border: 1px solid #3c4f48; border-radius: 7px;
    background: #182421; color: #e5efed; font-size: 14px; font-weight: 600; cursor: pointer;
  }
  button:hover:not(:disabled) { background: #263832; }
  button.primary { border: 0; background: #72d4a4; color: #13231b; }
  button.primary:hover:not(:disabled) { background: #8ae2b6; }
  button:disabled { cursor: default; opacity: .5; }
  #status { min-width: 80px; color: #bac8c2; font-size: 13px; }
  @media (max-width: 520px) { .settings { grid-template-columns: 1fr; } }
</style>
<script>
(() => {
  const text = document.getElementById("text");
  const voiceSelect = document.getElementById("voice");
  const rate = document.getElementById("rate");
  const volume = document.getElementById("volume");
  const speakButton = document.getElementById("speak");
  const stopButton = document.getElementById("stop");
  const status = document.getElementById("status");
  const seed = __SEED__;
  const initialText = __TEXT__;
  const storageKey = "bolsuno-tts";
  const readStorage = (key) => { try { return sessionStorage.getItem(key); } catch (_) { return null; } };
  const writeStorage = (key, value) => { try { sessionStorage.setItem(key, value); } catch (_) {} };

  if (readStorage(`${storageKey}-seed`) !== seed) {
    text.value = initialText;
    writeStorage(`${storageKey}-seed`, seed);
    writeStorage(`${storageKey}-text`, initialText);
  } else {
    text.value = readStorage(`${storageKey}-text`) ?? initialText;
  }
  text.addEventListener("input", () => writeStorage(`${storageKey}-text`, text.value));

  const updateValues = () => {
    document.getElementById("rate-value").value = `${Number(rate.value).toFixed(1)}x`;
    document.getElementById("volume-value").value = `${Math.round(Number(volume.value) * 100)}%`;
  };
  rate.addEventListener("input", updateValues);
  volume.addEventListener("input", updateValues);
  updateValues();

  if (!("speechSynthesis" in window) || !("SpeechSynthesisUtterance" in window)) {
    status.textContent = "Speech is not supported by this browser.";
    speakButton.disabled = true;
    return;
  }

  const synthesis = window.speechSynthesis;
  let voices = [];
  const loadVoices = () => {
    const selected = voiceSelect.value;
    voices = synthesis.getVoices();
    voiceSelect.replaceChildren(new Option("System default", ""));
    for (const voice of voices) {
      voiceSelect.add(new Option(`${voice.name} (${voice.lang})`, voice.voiceURI));
    }
    if (voices.some((voice) => voice.voiceURI === selected)) voiceSelect.value = selected;
  };
  loadVoices();
  synthesis.addEventListener("voiceschanged", loadVoices);

  speakButton.addEventListener("click", () => {
    const value = text.value.trim();
    if (!value) { status.textContent = "Enter some text first."; return; }
    synthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(value);
    utterance.rate = Number(rate.value);
    utterance.volume = Number(volume.value);
    utterance.voice = voices.find((voice) => voice.voiceURI === voiceSelect.value) || null;
    utterance.onstart = () => { status.textContent = "Speaking..."; };
    utterance.onend = () => {
      status.textContent = "Finished";
      stopButton.disabled = true;
      speakButton.disabled = false;
    };
    utterance.onerror = (event) => {
      if (event.error !== "canceled") status.textContent = `Speech failed: ${event.error}`;
      stopButton.disabled = true;
      speakButton.disabled = false;
    };
    speakButton.disabled = true;
    stopButton.disabled = false;
    status.textContent = "Starting...";
    synthesis.speak(utterance);
  });

  stopButton.addEventListener("click", () => {
    synthesis.cancel();
    status.textContent = "Speech stopped";
    stopButton.disabled = true;
    speakButton.disabled = false;
  });
  document.getElementById("clear").addEventListener("click", () => {
    synthesis.cancel();
    text.value = "";
    writeStorage(`${storageKey}-text`, "");
    status.textContent = "";
    stopButton.disabled = true;
    speakButton.disabled = false;
  });
})();
</script>
"""
    html = (
      html.replace("__SEED__", safe_seed)
        .replace("__RATE__", f"{initial_rate:.2f}")
        .replace("__VOLUME__", f"{initial_volume:.2f}")
      .replace("__TEXT__", safe_text)
    )
    components.html(html, height=500, scrolling=True)