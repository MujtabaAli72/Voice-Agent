import streamlit as st
import requests
import datetime as dt
import threading
import queue
import os
import tempfile
import time

st.set_page_config(
    page_title="Elya Voice Agent",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
/* ── layout ── */
.block-container { padding-top: 1.5rem; }

/* ── chat bubbles ── */
.bubble-wrap-ai  { display:flex; justify-content:flex-start; margin:6px 0; }
.bubble-wrap-user{ display:flex; justify-content:flex-end;   margin:6px 0; }
.bubble {
    max-width: 78%;
    padding: 10px 15px;
    font-size: 14px;
    line-height: 1.55;
    border-radius: 16px;
}
.bubble-ai   { background:#f0f2f6; color:#1a1a2e; border-bottom-left-radius:4px; }
.bubble-user { background:#1565c0; color:#ffffff; border-bottom-right-radius:4px; }

/* ── voice panel ── */
.voice-card {
    background: #f8f9fc;
    border: 1px solid #e0e3ef;
    border-radius: 16px;
    padding: 28px 20px;
    text-align: center;
}
.mic-ring {
    width: 86px; height: 86px;
    border-radius: 50%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 34px;
    cursor: pointer;
    margin-bottom: 14px;
}
.mic-idle      { background:#e8eaf6; border:2px solid #c5cae9; }
.mic-listening { background:#ffebee; border:2px solid #ef9a9a; animation:pulse 1.2s infinite; }
.mic-processing{ background:#fff8e1; border:2px solid #ffe082; }
.mic-speaking  { background:#e8f5e9; border:2px solid #a5d6a7; }
@keyframes pulse {
    0%,100%{ box-shadow:0 0 0 0 rgba(239,83,80,.25); }
    50%    { box-shadow:0 0 0 14px rgba(239,83,80,0); }
}
.status-text { font-size:13px; font-weight:600; letter-spacing:.04em; }
.status-idle      { color:#9e9e9e; }
.status-listening { color:#e53935; }
.status-processing{ color:#f9a825; }
.status-speaking  { color:#43a047; }

/* ── waveform bars ── */
.wave { display:flex; align-items:center; justify-content:center; gap:4px; height:36px; margin:10px 0; }
.wave-bar {
    width:4px; border-radius:3px;
    background:#c5cae9;
    transition: height .1s;
}
.wave-active .wave-bar { background:#1565c0; }
.wave-active .wave-bar:nth-child(1){animation:wv .7s -.3s infinite;}
.wave-active .wave-bar:nth-child(2){animation:wv .7s -.2s infinite;}
.wave-active .wave-bar:nth-child(3){animation:wv .7s -.1s infinite;}
.wave-active .wave-bar:nth-child(4){animation:wv .7s  .0s infinite;}
.wave-active .wave-bar:nth-child(5){animation:wv .7s -.15s infinite;}
.wave-active .wave-bar:nth-child(6){animation:wv .7s -.25s infinite;}
.wave-active .wave-bar:nth-child(7){animation:wv .7s -.05s infinite;}
@keyframes wv {
    0%,100%{ height:5px; }
    50%    { height:30px; }
}

/* ── sidebar ── */
section[data-testid="stSidebar"] > div:first-child { padding-top: 1.2rem; }

/* ── metric cards ── */
[data-testid="stMetric"] {
    background:#f8f9fc;
    border:1px solid #e0e3ef;
    border-radius:12px;
    padding:14px 16px;
}
</style>
""", unsafe_allow_html=True)

# ─── session state ────────────────────────────────────────────────────────────
def _init():
    defaults = {
        "messages": [{"role":"ai","text":"Hello! I'm Elya. How can I help you today?","ts":_now()}],
        "voice_status": "idle",   # idle | listening | processing | speaking
        "page": "Home",
        "base_url": "http://localhost:4444",
        "tts_engine": "pyttsx3",
        "stt_engine": "google",
        "last_transcript": "",
        "groq_api_key": os.getenv("GROQ_API_KEY",""),
    }
    for k,v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def _now():
    return dt.datetime.now().strftime("%H:%M")

_init()

# ─── helpers ──────────────────────────────────────────────────────────────────
def _check_backend():
    try:
        requests.get(st.session_state.base_url, timeout=1.5)
        return True
    except:
        return False

def _list_appts(date: dt.date):
    try:
        r = requests.post(
            f"{st.session_state.base_url}/list_appointments/",
            json={"date": date.isoformat()}, timeout=4
        )
        return r.json() if r.ok else []
    except:
        return []

def _schedule(name, reason, start_dt):
    payload = {
        "patient_name": name.strip(),
        "reason": reason.strip() or None,
        "start_time": start_dt.isoformat(),
    }
    r = requests.post(
        f"{st.session_state.base_url}/schedule_appointment/",
        json=payload, timeout=10
    )
    r.raise_for_status()
    return r.json()

def _cancel(name, date):
    r = requests.post(
        f"{st.session_state.base_url}/cancel_appointment/",
        json={"patient_name": name.strip(), "date": date.isoformat()},
        timeout=10
    )
    r.raise_for_status()
    return r.json()

# ─── AI response ──────────────────────────────────────────────────────────────
def _ai_response(user_text: str) -> str:
    """Call Groq LLM or fall back to rule-based responses."""
    key = st.session_state.groq_api_key
    if key:
        try:
            from groq import Groq
            client = Groq(api_key=key)
            history = [
                {"role":"system","content":(
                    "You are Elya, a friendly hospital appointment assistant. "
                    "Help patients book, cancel, or check appointments. "
                    "Keep replies concise (2-3 sentences max)."
                )}
            ]
            for m in st.session_state.messages[-8:]:
                history.append({"role":"user" if m["role"]=="user" else "assistant","content":m["text"]})
            history.append({"role":"user","content":user_text})
            resp = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=history,
                max_tokens=200,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            return f"[Groq error: {e}]"

    # ── rule-based fallback (no API key needed) ──
    t = user_text.lower()
    if any(w in t for w in ["book","schedule","appointment","appoint"]):
        return "I'd be happy to book an appointment. Please fill in the form on the left, or tell me the patient name, date and time."
    if any(w in t for w in ["cancel","cancell"]):
        return "To cancel an appointment, please provide the patient name and the date. I'll take care of it right away."
    if any(w in t for w in ["list","check","show","today","tomorrow"]):
        return "I can show you the appointments. Use the 'list appointments' section below, or let me know which date you'd like to check."
    if any(w in t for w in ["hello","hi","hey","good"]):
        return "Hello! I'm Elya, your hospital voice assistant. How can I help you today?"
    if any(w in t for w in ["thank","thanks"]):
        return "You're welcome! Is there anything else I can help you with?"
    return "I'm here to help with appointment scheduling, cancellations, and inquiries. What would you like to do?"

# ─── speech-to-text ───────────────────────────────────────────────────────────
def _stt() -> str:
    """Record from mic and return transcript. Returns '' on failure."""
    try:
        import speech_recognition as sr
        r = sr.Recognizer()
        r.energy_threshold = 300
        r.dynamic_energy_threshold = True
        with sr.Microphone() as src:
            r.adjust_for_ambient_noise(src, duration=0.5)
            audio = r.listen(src, timeout=8, phrase_time_limit=15)
        engine = st.session_state.stt_engine
        if engine == "google":
            return r.recognize_google(audio)
        elif engine == "sphinx":
            return r.recognize_sphinx(audio)
        else:
            return r.recognize_google(audio)
    except Exception as e:
        return f"__error__{e}"

# ─── text-to-speech ───────────────────────────────────────────────────────────
def _tts(text: str):
    """Speak text. Tries pyttsx3 first, then gTTS."""
    engine = st.session_state.tts_engine
    if engine == "pyttsx3":
        try:
            import pyttsx3
            eng = pyttsx3.init()
            eng.setProperty("rate", 165)
            eng.say(text)
            eng.runAndWait()
            eng.stop()
            return
        except Exception:
            pass
    # gTTS fallback — plays via st.audio
    try:
        from gtts import gTTS
        import pygame, io
        tts = gTTS(text=text, lang="en", slow=False)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
        st.audio(buf, format="audio/mp3", autoplay=True)
    except Exception:
        pass

# ─── sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎙️ Elya")
    st.caption("AI Voice Agent")
    st.divider()

    for page in ["Home", "Chat History", "Settings"]:
        icon = {"Home":"🏠","Chat History":"💬","Settings":"⚙️"}[page]
        if st.button(f"{icon}  {page}", use_container_width=True, key=f"nav_{page}"):
            st.session_state.page = page
            st.rerun()

    st.divider()
    online = _check_backend()
    if online:
        st.success("Backend online ✅")
    else:
        st.error("Backend offline ❌")
    st.caption("Backend URL")
    new_url = st.text_input("", value=st.session_state.base_url, label_visibility="collapsed")
    if new_url != st.session_state.base_url:
        st.session_state.base_url = new_url
        st.rerun()

    if st.session_state.groq_api_key:
        st.success("Groq API key set ✅")
    else:
        st.warning("No Groq key — using rule-based AI")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: HOME
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "Home":

    today = dt.date.today()
    appts = _list_appts(today)
    total   = len(appts)
    confirmed = sum(1 for a in appts if not a.get("canceled"))
    canceled  = total - confirmed
    n_msgs    = len(st.session_state.messages)

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("📅 Today's appointments", total)
    c2.metric("✅ Confirmed", confirmed)
    c3.metric("❌ Canceled", canceled)
    c4.metric("💬 Chat turns", n_msgs)

    st.markdown("---")
    voice_col, chat_col = st.columns([1,1], gap="medium")

    # ── VOICE PANEL ──────────────────────────────────────────────────────────
    with voice_col:
        status = st.session_state.voice_status
        icon_class = {
            "idle":"mic-idle","listening":"mic-listening",
            "processing":"mic-processing","speaking":"mic-speaking"
        }[status]
        status_label = {
            "idle":"● Idle","listening":"● Listening...","processing":"● Processing...","speaking":"● Speaking..."
        }[status]
        status_cls = {
            "idle":"status-idle","listening":"status-listening",
            "processing":"status-processing","speaking":"status-speaking"
        }[status]
        wave_cls = "wave-active" if status in ("listening","speaking") else ""

        st.markdown(f"""
        <div class="voice-card">
          <div class="mic-ring {icon_class}">🎙️</div>
          <br>
          <span class="status-text {status_cls}">{status_label}</span>
          <div class="wave {wave_cls}">
            {''.join('<div class="wave-bar" style="height:8px"></div>' for _ in range(7))}
          </div>
          <p style="font-size:12px;color:#9e9e9e;margin-top:8px">
            {"Click 'Start listening' to speak" if status=="idle" else "Recording your voice..."}
          </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("")

        # mic button
        if status == "idle":
            if st.button("🎙️ Start listening", use_container_width=True, type="primary"):
                st.session_state.voice_status = "listening"
                st.rerun()
        else:
            if st.button("⏹️ Stop", use_container_width=True):
                st.session_state.voice_status = "idle"
                st.rerun()

        # when listening → capture in same run
        if status == "listening":
            with st.spinner("Listening... speak now"):
                result = _stt()
            if result.startswith("__error__"):
                err = result.replace("__error__","")
                st.error(f"Mic error: {err}")
                st.info("💡 Tip: Make sure your microphone is connected and browser has permission.")
                st.session_state.voice_status = "idle"
                st.rerun()
            else:
                st.session_state.last_transcript = result
                st.session_state.messages.append({"role":"user","text":result,"ts":_now()})
                st.session_state.voice_status = "processing"
                st.rerun()

        if status == "processing":
            with st.spinner("Getting AI response..."):
                reply = _ai_response(st.session_state.messages[-1]["text"])
            st.session_state.messages.append({"role":"ai","text":reply,"ts":_now()})
            st.session_state.voice_status = "speaking"
            st.rerun()

        if status == "speaking":
            with st.spinner("Speaking..."):
                _tts(st.session_state.messages[-1]["text"])
            st.session_state.voice_status = "idle"
            st.rerun()

        if st.session_state.last_transcript:
            st.markdown(f"**Last heard:** _{st.session_state.last_transcript}_")

        st.markdown("---")
        st.markdown("**📋 Book appointment**")
        with st.form("book_form"):
            name     = st.text_input("Patient name")
            reason   = st.text_input("Reason")
            appt_date= st.date_input("Date", value=today + dt.timedelta(days=1))
            appt_time= st.time_input("Time", value=dt.time(9,0))
            if st.form_submit_button("Book ✅", use_container_width=True):
                if not name.strip():
                    st.error("Patient name is required.")
                elif not online:
                    st.error("Backend is offline.")
                else:
                    try:
                        start_dt = dt.datetime.combine(appt_date, appt_time)
                        _schedule(name, reason, start_dt)
                        msg = f"Appointment booked for {name} on {appt_date} at {appt_time.strftime('%H:%M')}."
                        st.success(msg)
                        st.session_state.messages.append({"role":"ai","text":msg,"ts":_now()})
                    except Exception as e:
                        st.error(f"Booking failed: {e}")

        st.markdown("**❌ Cancel appointment**")
        with st.form("cancel_form"):
            cname = st.text_input("Patient name", key="cname")
            cdate = st.date_input("Date", key="cdate", value=today)
            if st.form_submit_button("Cancel appointment", use_container_width=True):
                if not cname.strip():
                    st.error("Patient name is required.")
                elif not online:
                    st.error("Backend is offline.")
                else:
                    try:
                        data = _cancel(cname, cdate)
                        n = data.get("canceled_count",0)
                        msg = f"Canceled {n} appointment(s) for {cname} on {cdate}."
                        st.success(msg)
                        st.session_state.messages.append({"role":"ai","text":msg,"ts":_now()})
                    except Exception as e:
                        st.error(f"Cancel failed: {e}")

    # ── CHAT PANEL ───────────────────────────────────────────────────────────
    with chat_col:
        st.markdown("#### 💬 Chat with Elya")

        chat_html = ""
        for m in st.session_state.messages:
            ts = m.get("ts","")
            if m["role"] == "ai":
                chat_html += f"""
                <div class="bubble-wrap-ai">
                  <div>
                    <div class="bubble bubble-ai">{m['text']}</div>
                    <div style="font-size:11px;color:#bbb;margin:2px 4px">Elya · {ts}</div>
                  </div>
                </div>"""
            else:
                chat_html += f"""
                <div class="bubble-wrap-user">
                  <div>
                    <div class="bubble bubble-user">{m['text']}</div>
                    <div style="font-size:11px;color:#bbb;margin:2px 4px;text-align:right">You · {ts}</div>
                  </div>
                </div>"""

        st.markdown(f"""
        <div style="
            height:460px;overflow-y:auto;padding:12px;
            background:#fff;border:1px solid #e0e3ef;
            border-radius:14px;margin-bottom:12px;
        ">{chat_html}</div>
        """, unsafe_allow_html=True)

        with st.form("chat_form", clear_on_submit=True):
            cols = st.columns([5,1])
            user_input = cols[0].text_input("", placeholder="Type a message...", label_visibility="collapsed")
            send = cols[1].form_submit_button("Send")
            if send and user_input.strip():
                st.session_state.messages.append({"role":"user","text":user_input.strip(),"ts":_now()})
                reply = _ai_response(user_input.strip())
                st.session_state.messages.append({"role":"ai","text":reply,"ts":_now()})
                st.rerun()

        st.markdown("**📅 List appointments**")
        check_date = st.date_input("Date to check", value=today, key="list_date")
        if st.button("Show appointments", use_container_width=True):
            if not online:
                st.error("Backend offline.")
            else:
                data = _list_appts(check_date)
                if data:
                    import pandas as pd
                    df = pd.DataFrame(data)[["patient_name","reason","start_time","canceled"]]
                    df.columns = ["Patient","Reason","Time","Canceled"]
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.info("No appointments found for that date.")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: CHAT HISTORY
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "Chat History":
    st.markdown("### 💬 Chat history")
    if not st.session_state.messages:
        st.info("No messages yet.")
    else:
        for m in st.session_state.messages:
            role = "You" if m["role"] == "user" else "🤖 Elya"
            ts   = m.get("ts","")
            st.markdown(f"**{role}** `{ts}` — {m['text']}")
        st.markdown("---")
        if st.button("🗑️ Clear history", type="secondary"):
            st.session_state.messages = [{"role":"ai","text":"Chat cleared. How can I help you?","ts":_now()}]
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: SETTINGS
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "Settings":
    st.markdown("### ⚙️ Settings")

    with st.form("settings_form"):
        st.markdown("**AI & API**")
        groq_key = st.text_input(
            "Groq API key",
            value=st.session_state.groq_api_key,
            type="password",
            help="Get a free key at console.groq.com"
        )
        st.markdown("**Voice**")
        tts = st.selectbox("Text-to-speech engine", ["pyttsx3","gTTS"], index=0 if st.session_state.tts_engine=="pyttsx3" else 1)
        stt = st.selectbox("Speech-to-text engine", ["google","sphinx"], index=0 if st.session_state.stt_engine=="google" else 1)

        st.markdown("**Backend**")
        url = st.text_input("Backend URL", value=st.session_state.base_url)

        if st.form_submit_button("Save settings ✅", use_container_width=True):
            st.session_state.groq_api_key = groq_key
            st.session_state.tts_engine   = tts
            st.session_state.stt_engine   = stt
            st.session_state.base_url     = url
            if groq_key:
                os.environ["GROQ_API_KEY"] = groq_key
            st.success("Settings saved!")

    st.markdown("---")
    st.markdown("**Install missing dependencies**")
    st.code("""pip install speechrecognition pyttsx3 gtts groq pyaudio
# Windows extra for PyAudio:
pip install pipwin && pipwin install pyaudio""", language="bash")

    st.markdown("**Run the app**")
    st.code("streamlit run app.py", language="bash")