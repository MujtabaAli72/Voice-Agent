import io
import os
import datetime as dt

import requests
import streamlit as st

st.set_page_config(
    page_title="CareSync AI",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body, .stApp { background: #0a0a12 !important; font-family: 'Inter', sans-serif !important; color: #e8e8f0 !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }
button[data-testid="collapsedControl"] { display: none !important; }
section[data-testid="stSidebar"] { background: rgba(255,255,255,0.025) !important; border-right: 1px solid rgba(255,255,255,0.07) !important; min-width: 220px !important; max-width: 220px !important; }
section[data-testid="stSidebar"] > div { padding: 0 !important; }
section[data-testid="stSidebar"] .stButton > button { background: transparent !important; border: none !important; color: rgba(255,255,255,0.45) !important; text-align: left !important; padding: 9px 16px !important; border-radius: 10px !important; font-size: 13px !important; font-family: 'Inter', sans-serif !important; width: 100% !important; transition: all 0.2s !important; }
section[data-testid="stSidebar"] .stButton > button:hover { background: rgba(255,255,255,0.06) !important; color: rgba(255,255,255,0.85) !important; }
[data-testid="stMetric"] { background: rgba(255,255,255,0.04) !important; border: 1px solid rgba(255,255,255,0.08) !important; border-radius: 14px !important; padding: 14px 18px !important; transition: transform 0.2s, border-color 0.2s !important; }
[data-testid="stMetric"]:hover { transform: translateY(-2px) !important; border-color: rgba(124,58,237,0.35) !important; }
[data-testid="stMetricLabel"] > div { color: rgba(255,255,255,0.35) !important; font-size: 11px !important; }
[data-testid="stMetricValue"] > div { color: #e8e8f0 !important; font-size: 24px !important; font-weight: 600 !important; }
.stTextInput > div > div > input, .stDateInput > div > div > input, .stTimeInput > div > div > input { background: rgba(255,255,255,0.04) !important; border: 1px solid rgba(255,255,255,0.1) !important; border-radius: 10px !important; color: #e8e8f0 !important; font-family: 'Inter', sans-serif !important; font-size: 13px !important; }
.stTextInput > div > div > input:focus { border-color: rgba(124,58,237,0.6) !important; }
.stButton > button[kind="primary"] { background: linear-gradient(135deg,#7c3aed,#2563eb) !important; border: none !important; color: #fff !important; border-radius: 30px !important; font-size: 13px !important; font-weight: 500 !important; padding: 10px 28px !important; transition: opacity 0.2s, transform 0.2s !important; }
.stButton > button[kind="primary"]:hover { opacity: 0.85 !important; transform: scale(1.02) !important; }
.stButton > button[kind="secondary"] { background: rgba(239,68,68,0.12) !important; border: 1px solid rgba(239,68,68,0.3) !important; color: #f87171 !important; border-radius: 30px !important; font-size: 13px !important; font-weight: 500 !important; padding: 10px 28px !important; }
.stButton > button[kind="secondary"]:hover { background: rgba(239,68,68,0.2) !important; }
.stSelectbox label, .stTextInput label, .stDateInput label, .stTimeInput label { color: rgba(255,255,255,0.45) !important; font-size: 12px !important; }
.chat-scroll { height: 380px; overflow-y: auto; padding: 12px 4px; display: flex; flex-direction: column; gap: 10px; scrollbar-width: thin; scrollbar-color: rgba(255,255,255,0.1) transparent; }
.chat-scroll::-webkit-scrollbar { width: 3px; }
.chat-scroll::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 2px; }
.bw-ai  { display:flex; justify-content:flex-start; margin:4px 0; }
.bw-user{ display:flex; justify-content:flex-end; margin:4px 0; }
.bubble { max-width:80%; padding:10px 15px; font-size:13px; line-height:1.55; border-radius:16px; }
.bai    { background:rgba(255,255,255,0.06); border:1px solid rgba(255,255,255,0.09); color:rgba(255,255,255,0.82); border-bottom-left-radius:4px; }
.buser  { background:linear-gradient(135deg,#7c3aed,#2563eb); color:#fff; border-bottom-right-radius:4px; }
.bmeta  { font-size:10px; color:rgba(255,255,255,0.22); margin-top:3px; }
.bmeta-r{ text-align:right; }
.voice-card { background: rgba(255,255,255,0.025); border: 1px solid rgba(255,255,255,0.07); border-radius: 18px; padding: 28px 20px; text-align: center; }
.mic-outer { width: 100px; height: 100px; border-radius: 50%; margin: 0 auto 14px; display: flex; align-items: center; justify-content: center; transition: all 0.3s; }
.mic-idle       { background:rgba(124,58,237,0.1);  border:2px solid rgba(124,58,237,0.35); }
.mic-listening  { background:rgba(239,68,68,0.12);  border:2px solid rgba(239,68,68,0.5); animation:mpulse 1.2s infinite; }
.mic-processing { background:rgba(245,158,11,0.12); border:2px solid rgba(245,158,11,0.5); }
.mic-speaking   { background:rgba(52,211,153,0.12); border:2px solid rgba(52,211,153,0.5); }
@keyframes mpulse { 0%,100%{ box-shadow:0 0 0 0 rgba(239,68,68,0.3); } 50%{ box-shadow:0 0 0 20px rgba(239,68,68,0); } }
.mic-icon-text { font-size: 32px; }
.wave { display:flex; align-items:center; justify-content:center; gap:4px; height:34px; margin:10px 0; }
.wb   { width:3px; border-radius:3px; background:rgba(255,255,255,0.1); }
.wave-on .wb { background:#7c3aed; }
.wave-on .wb:nth-child(1){ animation:wv .7s -.30s infinite; }
.wave-on .wb:nth-child(2){ animation:wv .7s -.20s infinite; }
.wave-on .wb:nth-child(3){ animation:wv .7s -.10s infinite; }
.wave-on .wb:nth-child(4){ animation:wv .7s  .00s infinite; }
.wave-on .wb:nth-child(5){ animation:wv .7s -.15s infinite; }
.wave-on .wb:nth-child(6){ animation:wv .7s -.25s infinite; }
.wave-on .wb:nth-child(7){ animation:wv .7s -.05s infinite; }
@keyframes wv { 0%,100%{height:4px} 50%{height:26px} }
.st-idle       { color:rgba(255,255,255,0.35); font-size:12px; font-weight:500; }
.st-listening  { color:#f87171; font-size:12px; font-weight:500; }
.st-processing { color:#fbbf24; font-size:12px; font-weight:500; }
.st-speaking   { color:#34d399; font-size:12px; font-weight:500; }
.transcript-box { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07); border-radius: 10px; padding: 10px 14px; font-size: 12px; color: rgba(255,255,255,0.4); min-height: 44px; line-height: 1.5; margin-top: 8px; font-style: italic; }
.err-box { background: rgba(239,68,68,0.08); border: 1px solid rgba(239,68,68,0.25); border-radius: 10px; padding: 10px 14px; font-size: 12px; color: #f87171; margin-top:8px; }
hr { border-color: rgba(255,255,255,0.07) !important; margin: 18px 0 !important; }
[data-testid="stDataFrame"] { background: rgba(255,255,255,0.03) !important; border-radius: 12px !important; border: 1px solid rgba(255,255,255,0.08) !important; }
</style>
""", unsafe_allow_html=True)

# ── session state ──────────────────────────────────────────────────────────
_DEFAULTS = {
    "messages": [{"role":"ai","text":"Hello! I'm CareSync AI, your smart hospital assistant. I can help you book, cancel, or check appointments. How can I help you today?","ts":""}],
    "voice_status": "idle",
    "voice_error": "",
    "page": "Home",
    "base_url": "http://localhost:4444",
    "tts_engine": "gtts",
    "stt_engine": "google",
    "last_transcript": "",
    "groq_api_key": os.getenv("GROQ_API_KEY",""),
    "pending_tts": "",
}
for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ── helpers ────────────────────────────────────────────────────────────────
def _now():
    return dt.datetime.now().strftime("%H:%M")

def _push(role, text):
    st.session_state.messages.append({"role": role, "text": text, "ts": _now()})

# ── backend ────────────────────────────────────────────────────────────────
def _online():
    try:
        requests.get(st.session_state.base_url, timeout=2)
        return True
    except Exception:
        return False

def _list_appts(date):
    try:
        r = requests.post(
            f"{st.session_state.base_url}/list_appointments/",
            json={"date": date.isoformat()}, timeout=5
        )
        r.raise_for_status()
        data = r.json()
        return data if isinstance(data, list) else []
    except requests.exceptions.ConnectionError:
        st.error("Cannot reach backend — is it running on port 4444?")
    except requests.exceptions.Timeout:
        st.error("Backend timed out.")
    except Exception as e:
        st.error(f"Error: {e}")
    return []

def _schedule(name, reason, start_dt):
    try:
        r = requests.post(
            f"{st.session_state.base_url}/schedule_appointment/",
            json={"patient_name": name.strip(), "reason": reason.strip() or None, "start_time": start_dt.isoformat()},
            timeout=10
        )
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error("Cannot reach backend.")
    except requests.exceptions.Timeout:
        st.error("Backend timed out while booking.")
    except Exception as e:
        st.error(f"Booking failed: {e}")
    return None

def _cancel_appt(name, date):
    try:
        r = requests.post(
            f"{st.session_state.base_url}/cancel_appointment/",
            json={"patient_name": name.strip(), "date": date.isoformat()},
            timeout=10
        )
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error("Cannot reach backend.")
    except requests.exceptions.Timeout:
        st.error("Backend timed out while canceling.")
    except Exception as e:
        st.error(f"Cancel failed: {e}")
    return None

# ── AI response ────────────────────────────────────────────────────────────
_SYSTEM = (
    "You are CareSync AI, a professional and friendly hospital appointment assistant. "
    "Help patients book, cancel, or check appointments. "
    "Reply in 2-3 sentences max. Be warm and concise. Never say 'I am processing'."
)

_FALLBACK = [
    (["book","schedule","make an appointment"], "I'd be happy to book an appointment for you. Please fill in the patient name, date, and time in the Book Appointment form on the left."),
    (["cancel","remove","delete"],              "To cancel an appointment, use the Cancel Appointment form — just enter the patient name and date."),
    (["list","show","check","today","tomorrow"],"I can pull up appointments for any date. Use the List Appointments section and pick your date."),
    (["hello","hi","hey","good morning"],       "Hello! I'm CareSync AI, your hospital assistant. I can help you book, cancel, or view appointments — just ask!"),
    (["thank","thanks","appreciate"],           "You're very welcome! Is there anything else I can help you with today?"),
    (["help","what can you","capabilities"],    "I can book new appointments, cancel existing ones, or show the schedule for any date. What would you like to do?"),
    (["bye","goodbye","see you"],               "Take care! Feel free to come back anytime. Have a great day!"),
]

def _ai_response(text):
    key = st.session_state.groq_api_key
    if key:
        try:
            from groq import Groq
            client = Groq(api_key=key)
            history = [{"role":"system","content":_SYSTEM}]
            for m in st.session_state.messages[-10:]:
                history.append({"role":"user" if m["role"]=="user" else "assistant","content":m["text"]})
            history.append({"role":"user","content":text})
            resp = client.chat.completions.create(model="llama3-8b-8192", messages=history, max_tokens=200, temperature=0.6)
            return resp.choices[0].message.content.strip()
        except ImportError:
            pass
        except Exception as e:
            return f"AI error: {e}"
    t = text.lower()
    for keywords, reply in _FALLBACK:
        if any(k in t for k in keywords):
            return reply
    return "I'm here to help with hospital appointments. You can ask me to book, cancel, or list appointments, or use the forms directly."

# ── STT ────────────────────────────────────────────────────────────────────
def _stt():
    """Returns (transcript, error). One will be empty string."""
    try:
        import speech_recognition as sr
    except ImportError:
        return "", "SpeechRecognition not installed. Run: pip install SpeechRecognition"

    r = sr.Recognizer()
    r.energy_threshold = 300
    r.dynamic_energy_threshold = True
    r.pause_threshold = 0.8

    try:
        with sr.Microphone() as src:
            r.adjust_for_ambient_noise(src, duration=0.5)
            audio = r.listen(src, timeout=8, phrase_time_limit=20)
    except sr.WaitTimeoutError:
        return "", "No speech detected in 8 seconds — please try again."
    except OSError:
        return "", "Microphone not found or permission denied. Check your mic is connected."
    except Exception as e:
        return "", f"Microphone error: {e}"

    try:
        return r.recognize_google(audio).strip(), ""
    except sr.UnknownValueError:
        return "", "Could not understand speech. Please speak clearly and try again."
    except sr.RequestError as e:
        return "", f"Google STT unavailable: {e}. Check your internet connection."
    except Exception as e:
        return "", f"STT error: {e}"

# ── TTS ────────────────────────────────────────────────────────────────────
def _tts(text):
    if not text:
        return
    try:
        from gtts import gTTS
        buf = io.BytesIO()
        gTTS(text=text, lang="en", slow=False).write_to_fp(buf)
        buf.seek(0)
        st.audio(buf, format="audio/mp3", autoplay=True)
    except ImportError:
        st.warning("gTTS not installed. Run: pip install gTTS")
    except Exception as e:
        st.caption(f"TTS unavailable: {e}")

# ── HTML builders ──────────────────────────────────────────────────────────
def _chat_html():
    parts = []
    for m in st.session_state.messages:
        ts  = m.get("ts","")
        txt = m["text"].replace("<","&lt;").replace(">","&gt;")
        if m["role"] == "ai":
            parts.append(f'<div class="bw-ai"><div><div class="bubble bai">{txt}</div><div class="bmeta">CareSync AI · {ts}</div></div></div>')
        else:
            parts.append(f'<div class="bw-user"><div><div class="bubble buser">{txt}</div><div class="bmeta bmeta-r">You · {ts}</div></div></div>')
    return "".join(parts)

def _mic_html(status):
    cls   = {"idle":"mic-idle","listening":"mic-listening","processing":"mic-processing","speaking":"mic-speaking"}
    icons = {"idle":"🎙️","listening":"🔴","processing":"⏳","speaking":"🔊"}
    lbls  = {"idle":"● Idle — ready to listen","listening":"● Listening…","processing":"● Processing…","speaking":"● Speaking…"}
    scls  = {"idle":"st-idle","listening":"st-listening","processing":"st-processing","speaking":"st-speaking"}
    wave  = "wave-on" if status in ("listening","speaking") else ""
    bars  = "".join(f'<div class="wb" style="height:{h}px"></div>' for h in [5,9,5,14,7,5,11])
    hint  = "Click 'Start listening' below" if status == "idle" else "Voice capture active…"
    return (
        f'<div class="voice-card">'
        f'<div class="mic-outer {cls[status]}"><span class="mic-icon-text">{icons[status]}</span></div>'
        f'<div class="{scls[status]}">{lbls[status]}</div>'
        f'<div class="wave {wave}">{bars}</div>'
        f'<p style="font-size:11px;color:rgba(255,255,255,0.25);margin-top:4px">{hint}</p>'
        f'</div>'
    )

# ══════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="padding:20px 20px 16px;border-bottom:1px solid rgba(255,255,255,0.07);margin-bottom:8px">
      <div style="font-size:18px;font-weight:600;background:linear-gradient(135deg,#a78bfa,#60a5fa,#f472b6);-webkit-background-clip:text;-webkit-text-fill-color:transparent">CareSync AI</div>
      <div style="font-size:11px;color:rgba(255,255,255,0.3);margin-top:2px">Smart Hospital Assistant</div>
    </div>
    """, unsafe_allow_html=True)

    for _pg, _ic in [("Home","⬡"),("Chat History","◈"),("Settings","◎")]:
        if st.button(f"{_ic}  {_pg}", use_container_width=True, key=f"nav_{_pg}"):
            st.session_state.page = _pg
            st.rerun()

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    online = _online()
    _c,_b,_bd = ("#34d399","rgba(52,211,153,0.1)","rgba(52,211,153,0.25)") if online else ("#f87171","rgba(239,68,68,0.1)","rgba(239,68,68,0.25)")
    st.markdown(f'<div style="margin:0 12px;padding:6px 12px;background:{_b};border:1px solid {_bd};border-radius:20px;font-size:11px;color:{_c};text-align:center">{"● Backend online" if online else "● Backend offline"}</div>', unsafe_allow_html=True)
    if st.session_state.groq_api_key:
        st.markdown('<div style="margin:8px 12px 0;padding:6px 12px;background:rgba(96,165,250,0.1);border:1px solid rgba(96,165,250,0.2);border-radius:20px;font-size:11px;color:#60a5fa;text-align:center">● Groq AI active</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# HOME
# ══════════════════════════════════════════════════════════════════════════
if st.session_state.page == "Home":

    st.markdown("""
    <div style="padding:20px 24px 8px">
      <div style="font-size:22px;font-weight:600;background:linear-gradient(135deg,#a78bfa,#60a5fa,#f472b6);-webkit-background-clip:text;-webkit-text-fill-color:transparent">CareSync AI</div>
      <div style="font-size:13px;color:rgba(255,255,255,0.35);margin-top:2px">Smart Hospital Voice Agent</div>
    </div>
    """, unsafe_allow_html=True)

    today = dt.date.today()
    appts     = _list_appts(today) if online else []
    total     = len(appts)
    confirmed = sum(1 for a in appts if not a.get("canceled"))
    canceled  = total - confirmed

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("📅 Today's appointments", total)
    c2.metric("✅ Confirmed", confirmed)
    c3.metric("❌ Cancelled", canceled)
    c4.metric("💬 Chat turns", len(st.session_state.messages))

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    voice_col, chat_col = st.columns(2, gap="medium")

    # ── LEFT COLUMN ──────────────────────────────────────────────────────
    with voice_col:
        status = st.session_state.voice_status
        st.markdown(_mic_html(status), unsafe_allow_html=True)

        if st.session_state.voice_error:
            st.markdown(f'<div class="err-box">⚠ {st.session_state.voice_error}</div>', unsafe_allow_html=True)
            if st.button("Dismiss", key="dismiss_err"):
                st.session_state.voice_error = ""
                st.rerun()

        if status == "idle":
            if st.button("🎙️  Start listening", use_container_width=True, type="primary", key="btn_listen"):
                st.session_state.voice_status = "listening"
                st.session_state.voice_error  = ""
                st.rerun()
        else:
            if st.button("⏹️  Stop / Reset", use_container_width=True, type="secondary", key="btn_stop"):
                st.session_state.voice_status = "idle"
                st.session_state.voice_error  = ""
                st.rerun()

        # voice state machine
        if status == "listening":
            with st.spinner("🎙 Listening — speak now…"):
                transcript, err = _stt()
            if err:
                st.session_state.voice_error  = err
                st.session_state.voice_status = "idle"
                st.rerun()
            else:
                st.session_state.last_transcript = transcript
                _push("user", transcript)
                st.session_state.voice_status = "processing"
                st.rerun()

        elif status == "processing":
            with st.spinner("🤖 Getting response…"):
                reply = _ai_response(st.session_state.messages[-1]["text"])
            _push("ai", reply)
            st.session_state.pending_tts  = reply
            st.session_state.voice_status = "speaking"
            st.rerun()

        elif status == "speaking":
            _tts(st.session_state.pending_tts)
            st.session_state.pending_tts  = ""
            st.session_state.voice_status = "idle"
            # no rerun — keeps audio element alive

        if st.session_state.last_transcript:
            st.markdown(f'<div class="transcript-box">"{st.session_state.last_transcript}"</div>', unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)

        # book form
        st.markdown("<div style='font-size:12px;color:rgba(255,255,255,0.4);margin-bottom:10px;font-weight:500'>📋 BOOK APPOINTMENT</div>", unsafe_allow_html=True)
        with st.form("book_form", clear_on_submit=True):
            name      = st.text_input("Patient name")
            reason    = st.text_input("Reason (optional)")
            appt_date = st.date_input("Date", value=today + dt.timedelta(days=1))
            appt_time = st.time_input("Time", value=dt.time(9,0))
            if st.form_submit_button("Book appointment", use_container_width=True, type="primary"):
                if not name.strip():
                    st.error("Patient name is required.")
                elif not online:
                    st.error("Backend is offline — cannot book.")
                else:
                    result = _schedule(name, reason, dt.datetime.combine(appt_date, appt_time))
                    if result:
                        msg = f"Appointment booked for {name.strip()} on {appt_date} at {appt_time.strftime('%H:%M')}."
                        st.success(f"✅ {msg}")
                        _push("ai", msg)

        # cancel form
        st.markdown("<div style='font-size:12px;color:rgba(255,255,255,0.4);margin:14px 0 10px;font-weight:500'>❌ CANCEL APPOINTMENT</div>", unsafe_allow_html=True)
        with st.form("cancel_form", clear_on_submit=True):
            cname = st.text_input("Patient name", key="cname")
            cdate = st.date_input("Date", key="cdate")
            if st.form_submit_button("Cancel appointment", use_container_width=True, type="secondary"):
                if not cname.strip():
                    st.error("Patient name is required.")
                elif not online:
                    st.error("Backend is offline — cannot cancel.")
                else:
                    result = _cancel_appt(cname, cdate)
                    if result is not None:
                        n   = result.get("canceled_count", 0)
                        msg = (f"Cancelled {n} appointment(s) for {cname.strip()} on {cdate}."
                               if n > 0 else
                               f"No appointments found for {cname.strip()} on {cdate}.")
                        st.success(f"✅ {msg}") if n > 0 else st.info(f"ℹ️ {msg}")
                        _push("ai", msg)

    # ── RIGHT COLUMN ─────────────────────────────────────────────────────
    with chat_col:
        st.markdown("<div style='font-size:11px;font-weight:500;color:rgba(255,255,255,0.3);letter-spacing:.08em;margin-bottom:14px'>CHAT PANEL</div>", unsafe_allow_html=True)
        st.markdown(f'<div class="chat-scroll">{_chat_html()}</div>', unsafe_allow_html=True)

        with st.form("chat_form", clear_on_submit=True):
            cols = st.columns([5,1])
            # FIX: label must be non-empty in Streamlit 1.56+; hidden via label_visibility
            user_input = cols[0].text_input("Message", placeholder="Type a message…", label_visibility="collapsed")
            if cols[1].form_submit_button("Send", type="primary") and user_input.strip():
                _push("user", user_input.strip())
                _push("ai",   _ai_response(user_input.strip()))
                st.rerun()

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:12px;color:rgba(255,255,255,0.4);margin-bottom:10px;font-weight:500'>📅 LIST APPOINTMENTS</div>", unsafe_allow_html=True)
        check_date = st.date_input("Date to check", value=today, key="list_date")
        if st.button("Show appointments", use_container_width=True):
            if not online:
                st.error("Backend is offline.")
            else:
                data = _list_appts(check_date)
                if data:
                    import pandas as pd
                    df = pd.DataFrame(data)
                    show_cols = [c for c in ["patient_name","reason","start_time","canceled"] if c in df.columns]
                    df = df[show_cols]
                    df.columns = [c.replace("_"," ").title() for c in show_cols]
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.info(f"No appointments for {check_date}.")

# ══════════════════════════════════════════════════════════════════════════
# CHAT HISTORY
# ══════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "Chat History":
    st.markdown("<div style='font-size:18px;font-weight:500;margin-bottom:20px;padding:24px 24px 0'>Chat history</div>", unsafe_allow_html=True)
    if not st.session_state.messages:
        st.info("No messages yet.")
    else:
        st.markdown(f'<div class="chat-scroll" style="max-height:520px;height:520px;margin:0 24px">{_chat_html()}</div>', unsafe_allow_html=True)
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        if st.button("🗑️  Clear chat history", type="secondary"):
            st.session_state.messages = [{"role":"ai","text":"Chat cleared. How can I help?","ts":_now()}]
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════
# SETTINGS
# ══════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "Settings":
    st.markdown("<div style='font-size:18px;font-weight:500;margin-bottom:20px;padding:24px 24px 0'>Settings</div>", unsafe_allow_html=True)
    with st.form("settings_form"):
        st.markdown("<div style='font-size:12px;color:rgba(255,255,255,0.4);margin-bottom:10px;font-weight:500'>AI & API</div>", unsafe_allow_html=True)
        groq_key = st.text_input("Groq API key", value=st.session_state.groq_api_key, type="password", help="Free key at console.groq.com")
        st.markdown("<div style='font-size:12px;color:rgba(255,255,255,0.4);margin:14px 0 10px;font-weight:500'>VOICE ENGINES</div>", unsafe_allow_html=True)
        tts = st.selectbox("Text-to-speech", ["gtts","pyttsx3"], index=0 if st.session_state.tts_engine=="gtts" else 1, help="gTTS recommended.")
        stt = st.selectbox("Speech-to-text", ["google","sphinx"], index=0 if st.session_state.stt_engine=="google" else 1, help="Google STT requires internet.")
        st.markdown("<div style='font-size:12px;color:rgba(255,255,255,0.4);margin:14px 0 10px;font-weight:500'>BACKEND</div>", unsafe_allow_html=True)
        url = st.text_input("Backend URL", value=st.session_state.base_url)
        if st.form_submit_button("Save settings", use_container_width=True, type="primary"):
            st.session_state.groq_api_key = groq_key
            st.session_state.tts_engine   = tts
            st.session_state.stt_engine   = stt
            st.session_state.base_url     = url
            if groq_key:
                os.environ["GROQ_API_KEY"] = groq_key
            st.success("✅ Settings saved!")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:12px;color:rgba(255,255,255,0.4);margin-bottom:8px'>INSTALL DEPENDENCIES</div>", unsafe_allow_html=True)
    st.code("pip install streamlit requests speechrecognition gtts groq pandas", language="bash")
    st.markdown("<div style='font-size:12px;color:rgba(255,255,255,0.4);margin:12px 0 8px'>RUN APP</div>", unsafe_allow_html=True)
    st.code("streamlit run app.py", language="bash")