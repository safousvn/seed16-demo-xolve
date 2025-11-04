import os
import time
import streamlit as st
import requests

st.set_page_config(page_title="Seed 1.6 Auto Caller", layout="wide")

st.title("🚀 Seed 1.6 Auto Caller Dashboard")
st.caption("Automatically call Seed 1.6 Chat API and monitor token usage in real time.")

# --- Secrets ---
API_KEY = st.secrets.get("ARK_API_KEY", None)

if not API_KEY:
    st.error("❌ Missing ARK_API_KEY in Streamlit Secrets.")
    st.stop()

# --- Initialize ---
if "total_calls" not in st.session_state:
    st.session_state.total_calls = 0
if "total_tokens" not in st.session_state:
    st.session_state.total_tokens = 0

# --- API Settings ---
# API_URL = "https://ark.byteplusapi.com/v1/chat/completions"
API_URL = "https://ark.ap-southeast.bytepluses.com/api/v3/chat/completions"
MODEL_NAME = "seed-1-6-250915"

prompt_text = st.text_area("🧠 Prompt for Seed 1.6:", "Hello Seed, tell me something creative!", height=100)
interval = st.number_input("⏱ Call Interval (seconds):", 0.5, 60.0, 2.0)
auto_run = st.checkbox("Start Auto-Calling", value=False)

log_area = st.empty()

def call_seed_api():
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt_text}],
        "max_tokens": 100
    }

    start = time.time()
    response = requests.post(API_URL, headers=headers, json=data)
    latency = time.time() - start

    if response.status_code == 200:
        result = response.json()
        usage = result.get("usage", {})
        tokens = usage.get("total_tokens", 100)
        st.session_state.total_tokens += tokens
        st.session_state.total_calls += 1
        return {"ok": True, "latency": latency, "tokens": tokens}
    else:
        return {"ok": False, "error": response.text}

if auto_run:
    st.success("✅ Auto-calling is running...")
    progress = st.progress(0)
    for i in range(1000000):  # effectively infinite loop
        result = call_seed_api()
        if result["ok"]:
            log_area.write(f"✅ Call {st.session_state.total_calls} | Tokens: {result['tokens']} | Latency: {result['latency']:.2f}s")
        else:
            log_area.write(f"❌ Error: {result['error']}")
        st.metric("Total Calls", st.session_state.total_calls)
        st.metric("Total Tokens", st.session_state.total_tokens)
        time.sleep(interval)
        progress.progress((i % 100) / 100)
else:
    st.info("🟢 Click checkbox above to start auto-calling.")
