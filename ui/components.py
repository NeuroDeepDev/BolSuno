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