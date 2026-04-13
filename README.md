# 🏥 CareSync AI – Hospital Appointment Voice Agent

##  Overview

**CareSync AI** is an intelligent hospital appointment booking system that allows users to **book, cancel, and manage appointments** using both **voice commands** and **chat interface**.

This project combines **AI-powered conversation**, **voice interaction**, and a **modern dashboard UI** to create a seamless healthcare experience.

---

## ✨ Features

### 🎤 Voice Assistant

* Book appointments using voice
* Cancel appointments via speech
* Real-time speech-to-text processing
* AI-generated voice responses (Text-to-Speech)

### 💬 Chat System

* Smart AI assistant for conversation
* Book, cancel, and check appointments via chat
* Context-aware responses

### 📅 Appointment Management

* Book appointments online
* Cancel appointments easily
* View daily appointments
* Track:

  * Total appointments
  * Confirmed appointments
  * Cancelled appointments

###  Dashboard

* Modern and responsive UI (Streamlit)
* Real-time statistics
* Interactive panels
* Clean and professional design

---

##  Tech Stack

* **Frontend:** Streamlit
* **Backend:** FastAPI / Flask (API-based)
* **Database:** SQLite
* **AI Model:** Groq (LLaMA3)
* **Speech-to-Text:** SpeechRecognition
* **Text-to-Speech:** pyttsx3 / gTTS

---

##  Installation & Setup

### 1️⃣ Clone Repository

```bash
git clone https://github.com/YOUR-USERNAME/Voice-Agent.git
cd Voice-Agent
```

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate   # Windows
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Run Backend

```bash
python backend.py
```

### 5️⃣ Run Frontend

```bash
streamlit run app.py
```

---

##  How It Works

1. User speaks or types a request
2. AI processes the input
3. System interacts with backend APIs
4. Appointment is booked/cancelled/listed
5. Response is shown via chat and/or voice

---

##  Environment Variables

Create a `.env` file and add:

```env
GROQ_API_KEY=your_api_key_here
```

---

##  Future Improvements

* Whisper-based voice recognition
* ElevenLabs realistic voice
* Mobile app integration
* Multi-language support

---

##  Author

### **Mujtaba Ali**

📧 [m.elya1412@gmail.com](mailto:m.elya1412@gmail.com)

---

## ⭐ Support

If you like this project, give it a ⭐ on GitHub!
# Voice-Agent
