import os
import sqlite3
import mysql.connector
from mysql.connector import Error

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQLITE_DB_PATH = os.path.join(BASE_DIR, "scamguard.db")

def get_config():
    # 1. Try Streamlit Secrets (for Cloud deployments)
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "mysql" in st.secrets:
            sec = st.secrets["mysql"]
            return {
                "host": sec.get("host", "localhost"),
                "port": int(sec.get("port", 3306)),
                "user": sec.get("user", "root"),
                "password": sec.get("password", ""),
                "database": sec.get("database", "scamguard")
            }
    except Exception:
        pass

    # 2. Try Environment Variables / .env
    return {
        "host": os.getenv("MYSQL_HOST", "localhost"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", ""),
        "database": os.getenv("MYSQL_DATABASE", "scamguard")
    }

def seed_initial_history(conn_type="sqlite", conn=None):
    """Auto-seeds realistic past scam and safe communication scans so the app is never empty."""
    demo_records = [
        (
            "URGENT: Your SBI Bank account has been blocked due to pending KYC verification. Click http://bit.ly/sbi-kyc-update to verify your OTP immediately.",
            "",
            "scam",
            0.991,
            92,
            "CRITICAL",
            "Banking Impersonation Scam",
            "Urgency Trigger, Banking Verification, OTP Theft Pattern, Phishing Hyperlink"
        ),
        (
            "Audio Call Transcript: Good morning, this is Senior Inspector Sharma from CBI Crime Branch New Delhi. A parcel under your Aadhaar number containing illegal narcotics was seized at Mumbai Customs. You are placed under digital arrest.",
            "Good morning, this is Senior Inspector Sharma from CBI Crime Branch New Delhi. A parcel under your Aadhaar number containing illegal narcotics was seized at Mumbai Customs. You are placed under digital arrest.",
            "scam",
            0.965,
            88,
            "CRITICAL",
            "Digital Arrest & Police Extortion",
            "Legal Intimidation, Police Coercion, Law Enforcement Impersonation"
        ),
        (
            "Dear Consumer, your electricity power connection will be disconnected tonight at 9:30 PM due to unpaid monthly bill. Call our bill verification officer at 9876543210 immediately.",
            "",
            "scam",
            0.942,
            75,
            "HIGH",
            "Utility Disconnection Scam",
            "Urgent Deadline, Service Disconnection Threat, Fake Support Phone"
        ),
        (
            "Congratulations! You are selected for part-time Work from Home online job. Like YouTube videos and earn Rs 3,000 to 5,000 daily. Join Telegram channel t.me/fast_income_india.",
            "",
            "scam",
            0.978,
            68,
            "HIGH",
            "Job Phishing Scam",
            "High Returns Promise, Easy Work Offer, Unverified Messaging Link"
        ),
        (
            "Your HDFC Bank account XX1234 has been credited with INR 4,500.00 on 20-Oct-2026. Available balance: INR 38,200.00. - HDFC Bank",
            "",
            "safe",
            0.989,
            5,
            "LOW",
            "Legitimate Bank Notification",
            "Standard Transaction Pattern"
        ),
        (
            "Hey! The team meeting has been rescheduled to 4 PM in the conference room. Please bring your project presentation slides.",
            "",
            "safe",
            0.994,
            2,
            "LOW",
            "Legitimate Personal Communication",
            "Normal Conversational Pattern"
        )
    ]
    try:
        cur = conn.cursor()
        if conn_type == "sqlite":
            cur.executemany("""
                INSERT INTO analysis_history (
                    input_text, transcript, prediction, confidence, risk_score, risk_level, scam_type, indicators
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, demo_records)
        else:
            cur.executemany("""
                INSERT INTO analysis_history (
                    input_text, transcript, prediction, confidence, risk_score, risk_level, scam_type, indicators
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, demo_records)
        conn.commit()
        cur.close()
    except Exception as e:
        print(f"Seed error: {e}")

def init_sqlite():
    try:
        conn = sqlite3.connect(SQLITE_DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                input_text TEXT,
                transcript TEXT,
                prediction TEXT,
                confidence REAL,
                risk_score INTEGER,
                risk_level TEXT,
                scam_type TEXT,
                indicators TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

        # Auto-seed if empty
        cur.execute("SELECT COUNT(*) FROM analysis_history")
        count = cur.fetchone()[0]
        if count == 0:
            seed_initial_history("sqlite", conn)

        cur.close()
        conn.close()
        return True, "Database synchronized successfully (SQLite local database ready)."
    except Exception as e:
        return False, f"Database init error: {e}"

def init_db():
    cfg = get_config()
    try:
        conn = mysql.connector.connect(
            host=cfg["host"], port=cfg["port"],
            user=cfg["user"], password=cfg["password"],
            connection_timeout=3
        )
        cur = conn.cursor()
        cur.execute(f"CREATE DATABASE IF NOT EXISTS `{cfg['database']}`")
        cur.close()
        conn.close()

        conn = mysql.connector.connect(**cfg, connection_timeout=3)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                input_text LONGTEXT,
                transcript LONGTEXT,
                prediction VARCHAR(20),
                confidence FLOAT,
                risk_score INT,
                risk_level VARCHAR(20),
                scam_type VARCHAR(100),
                indicators TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

        # Auto-seed if empty
        cur.execute("SELECT COUNT(*) FROM analysis_history")
        count = cur.fetchone()[0]
        if count == 0:
            seed_initial_history("mysql", conn)

        cur.close()
        conn.close()
        return True, "MySQL database connected and synchronized successfully."
    except Error:
        # Fall back gracefully to SQLite if MySQL is unavailable
        return init_sqlite()

def save_analysis(message, prediction, risk_score, scam_type, indicators, transcript="", confidence=0.0, risk_level="LOW"):
    indicators_str = ", ".join(indicators) if isinstance(indicators, (list, tuple)) else str(indicators)
    cfg = get_config()
    
    # Try MySQL first (only if non-localhost host or live MySQL connection)
    try:
        conn = mysql.connector.connect(**cfg, connection_timeout=2)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO analysis_history (
                input_text, transcript, prediction, confidence, risk_score, risk_level, scam_type, indicators
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (message, transcript, str(prediction), float(confidence), int(risk_score), str(risk_level), str(scam_type), indicators_str))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception:
        pass

    # SQLite Fallback
    try:
        init_sqlite() # Ensure table and schema exist
        conn = sqlite3.connect(SQLITE_DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO analysis_history (
                input_text, transcript, prediction, confidence, risk_score, risk_level, scam_type, indicators
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (message, transcript, str(prediction), float(confidence), int(risk_score), str(risk_level), str(scam_type), indicators_str))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"SQLite save error: {e}")
        return False

def get_history(limit=100):
    cfg = get_config()
    # Try MySQL first
    try:
        conn = mysql.connector.connect(**cfg, connection_timeout=2)
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT *
            FROM analysis_history
            ORDER BY created_at DESC
            LIMIT %s;
        """, (limit,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        if rows:
            return rows
    except Exception:
        pass

    # SQLite Fallback
    try:
        init_sqlite() # Ensure table and seed exist
        conn = sqlite3.connect(SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("""
            SELECT id, input_text, transcript, prediction, confidence, risk_score, risk_level, scam_type, indicators, created_at
            FROM analysis_history
            ORDER BY created_at DESC
            LIMIT ?;
        """, (limit,))
        rows = [dict(row) for row in cur.fetchall()]
        cur.close()
        conn.close()
        return rows
    except Exception as e:
        print(f"SQLite fetch error: {e}")
        return []
