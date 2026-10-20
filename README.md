# 🛡️ AI ScamGuard

## 📌 Short Description
**AI ScamGuard** is an intelligent, full-stack cybersecurity application designed to detect, analyze, and protect users against fraudulent communications, social engineering attacks, and phone scam calls in real-time.

By combining **Supervised Machine Learning (TF-IDF + Scikit-Learn Classifiers)**, a **Weighted Rule-Based Heuristic Risk Engine**, and **Advanced Speech-to-Text NLP (OpenAI Whisper)**, AI ScamGuard provides comprehensive threat intelligence across both **Text Messages (SMS/WhatsApp/Emails)** and **Voice Audio Calls (Uploaded Files & Live Microphone Capture)**.

Users receive instant feedback including a **Risk Score (0–100)**, **Risk Assessment Level (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`)**, **Visual Keyword Highlighting**, **Extracted Spoken/Text Entities (Phones, URLs, Emails)**, **Scam Classification**, and **Actionable Safety Advice**.

---

## 🌟 Key Features

- **🏠 Command Center Dashboard**: Real-time system metrics, scan counters, threat distribution charts, and quick navigation.
- **📝 Text & 🎤 Audio Scam Detection (Equal Feature Parity)**:
  - **Machine Learning Classification**: Predicts `SCAM` vs `SAFE` status using trained Scikit-Learn pipelines.
  - **Transparent Risk Scoring (0–100)**: Calculates risk scores based on ML model predictions + weighted pattern rules.
  - **Risk Assessment Levels**: Categorizes threats into `CRITICAL` 🔴, `HIGH` 🟠, `MEDIUM` 🟡, and `LOW` 🟢 with animated progress bars.
  - **18+ Indicator Categories**: Detects OTP/CVV phishing, Urgency/Pressure, Bank/Financial requests, Impersonation, Lottery/Prize fraud, Crypto scams, QR Code tricks, and Remote Access Apps (AnyDesk, TeamViewer).
  - **🔍 Keyword Highlighting**: Visually highlights suspicious scam terms directly in the text/speech transcript using red badges.
  - **🌐 Entity Extraction**: Automatically extracts spoken or written Phone Numbers, Email Addresses, and Suspicious URLs.
  - **🧠 Threat Intelligence**: Categorizes scams into specific types (e.g. OTP Scam, Bank Scam, Phishing, Tech Support Scam, UPI Scam, Social Engineering).
  - **🛡️ Recommended Safety Action**: Provides immediate safety guidance tailored to the detected risk level.
- **🎙️ Audio & Speech Capabilities**:
  - Supports audio file formats (`.mp3`, `.wav`, `.m4a`, `.flac`, `.ogg`, `.aac`).
  - **Live Microphone Capture** using `streamlit-mic-recorder`.
  - **OpenAI Whisper** speech-to-text with automatic standalone FFmpeg binding (`imageio-ffmpeg`).
  - Automatic 16-bit PCM WAV conversion for non-standard audio encodings.
  - One-click transcript download (`.txt`).
- **📊 Interactive Analytics**: Plotly Express model comparison graphs (Accuracy, Precision, Recall, F1) and live scam distribution donut charts.
- **🗂 Audit History & Exports**: Persistent scan history logging with automatic local database storage and CSV export.
- **⚙ Settings & Personalization**: Configurable Whisper model sizes (`tiny`, `base`, `small`, `medium`), audio language selection, and Light/Dark theme toggle.

---

## 🏗 System Architecture & Pipeline

```
┌──────────────────────────┐
│  Audio / Text Input      │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐     ┌──────────────────────────┐
│  OpenAI Whisper STT      │ ──► │  SpeechRecognition       │
│  (with FFmpeg binding)   │     │  (PCM WAV Fallback)      │
└────────────┬─────────────┘     └────────────┬─────────────┘
             └──────────────┬─────────────────┘
                            │ (Transcribed Text / Input Text)
                            ▼
             ┌──────────────────────────────┐
             │ TF-IDF Vectorizer + ML Model │
             │ (scam_model.pkl)             │
             └──────────────┬───────────────┘
                            │
                            ▼
             ┌──────────────────────────────┐
             │ Weighted Risk Engine         │
             │ (18+ Pattern Regex Rules)    │
             └──────────────┬───────────────┘
                            │
                            ▼
             ┌──────────────────────────────┐
             │ Streamlit UI & Analytics     │
             │ (Database / Session History) │
             └──────────────┬───────────────┘
                            │
                            ▼
 ┌──────────────────────────────────────────────────────────┐
 │  FULL THREAT ANALYSIS REPORT (Text & Audio)              │
 │  • ML Prediction & Confidence %                          │
 │  • Risk Score (0-100) & Progress Bar                     │
 │  • Risk Level Badge (CRITICAL, HIGH, MEDIUM, LOW)        │
 │  • 🚨 Detected Threat Indicators                         │
 │  • 🔍 Highlighted Key Terms                              │
 │  • 🧠 Scam Classification                                │
 │  • 🌐 Extracted Entities (Phones, URLs, Emails)          │
 │  • 🛡️ Recommended Safety Guidance                        │
 └──────────────────────────────────────────────────────────┘
```

---

## 📁 File Structure

```
AI Scam guard project/
│
├── final_app.py              # Main Streamlit web application
├── database.py               # Database connector and history logger
├── requirements.txt          # Python project dependencies
├── packages.txt              # System dependencies for cloud deployment
├── README.md                 # Technical documentation & project guide
├── ScamGuard_ML.ipynb        # Jupyter Notebook for ML training & evaluation
│
├── models/
│   ├── scam_model.pkl        # Trained Scikit-Learn ML Model pipeline
│   └── model_results.csv     # Model evaluation benchmark metrics
│
└── data/
    └── messages.csv          # Training dataset for scam classification
```

---

## 🚀 Installation & Setup

### 1. Prerequisites
Ensure you have **Python 3.11 or higher** installed.

### 2. Install Dependencies
Open your terminal / PowerShell in the project directory and run:

```bash
pip install -r requirements.txt
```

*(Note: Audio decoding dependencies `imageio-ffmpeg`, `soundfile`, and `scipy` are included in `requirements.txt` to handle FFmpeg binary binding automatically).*

---

## 🗄 Database History Logging

**AI ScamGuard** includes built-in audit logging. Analysis history is automatically stored using an embedded SQLite database (`scamguard.db`) with zero manual setup required. An external database connection can optionally be configured via environment variables in a private `.env` file.

---

## 🏃 Running the Application

To start the Streamlit server:

```bash
streamlit run final_app.py
```

The web dashboard will automatically open in your default browser at **`http://localhost:8501`**.

---

## 🛠 Troubleshooting Audio Transcription

If you encounter audio processing issues:
- **Non-Standard WAV Files**: The application automatically converts non-PCM (e.g. 32-bit float or browser WebM blobs) into standard 16-bit PCM WAV.
- **FFmpeg Error on Windows**: Ensure `imageio-ffmpeg` is installed (`pip install imageio-ffmpeg`). The application automatically injects its FFmpeg binary path into `os.environ["PATH"]`.

---

## 🛡 Disclaimer

*AI ScamGuard is a research and educational prototype. Risk scores and threat classifications are probabilistic indicators derived from machine learning and heuristic rules. Users should independently verify suspicious communications through official bank or governmental channels.*
