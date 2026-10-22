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

def should_try_mysql(cfg):
    """Determines whether MySQL connection should be attempted based on environment."""
    if not cfg or not cfg.get("host"):
        return False
    # If host is not localhost, it's an external cloud database (e.g., TiDB, Aiven, Supabase)
    if cfg["host"] not in ("localhost", "127.0.0.1"):
        return True
    # If localhost, only try on Windows where developer may have local MySQL service
    return os.name == "nt"

def seed_initial_history(conn_type="sqlite", conn=None):
    """Auto-seeds authentic historical reports and test scans so the app is always populated."""
    demo_records = [
        (
            "WARNING: Your PC is infected with ransomware. Call Microsoft Support at +1-800-555-0199 or install AnyDesk immediately.",
            "",
            "scam",
            0.773402,
            100,
            "CRITICAL",
            "Tech Support Scam",
            "Urgency & Pressure, Impersonation, Crypto & Remote Access",
            "2026-09-01 13:07:47"
        ),
        (
            "c47459bfefe763f399de968edd245eb1.wav",
            "Hello Sir, I am from the State Bank of India. Your ATM is going to be closed. On your behalf I have a auto pv.",
            "safe",
            0.657729,
            20,
            "LOW",
            "Bank Scam",
            "Financial & Payments",
            "2026-08-07 15:12:21"
        ),
        (
            "URGENT! Your HDFC Bank account will be blocked today due to pending KYC. Click link http://bit.ly/bank-kyc and share your OTP immediately.",
            "",
            "scam",
            0.991737,
            100,
            "CRITICAL",
            "OTP Scam",
            "OTP / Verification, Urgency & Pressure, Threats & Legal Action, Financial & Payments, Suspicious Links",
            "2026-08-07 15:11:21"
        ),
        (
            "c47459bfefe763f399de968edd245eb1.wav",
            "Hello Sir, I am from the State Bank of India. Your ATM is going to be closed. On your behalf I have a auto pv.",
            "safe",
            0.657729,
            20,
            "LOW",
            "Bank Scam",
            "Financial & Payments",
            "2026-08-07 10:28:35"
        ),
        (
            "URGENT! Your HDFC Bank account will be blocked today due to pending KYC. Click link http://bit.ly/bank-kyc and share your OTP immediately.",
            "",
            "scam",
            0.991737,
            100,
            "CRITICAL",
            "OTP Scam",
            "OTP / Verification, Urgency & Pressure, Threats & Legal Action, Financial & Payments, Suspicious Links",
            "2026-08-07 10:27:39"
        ),
        (
            "c47459bfefe763f399de968edd245eb1.wav",
            "Hello Sir, I am from the State Bank of India. Your ATM is going to be closed. On your behalf I have a auto pv.",
            "safe",
            0.657729,
            20,
            "LOW",
            "Bank Scam",
            "Financial & Payments",
            "2026-08-06 23:37:33"
        ),
        (
            "URGENT! Your HDFC Bank account will be blocked today due to pending KYC. Click link http://bit.ly/bank-kyc and share your OTP immediately.",
            "",
            "scam",
            0.991737,
            100,
            "CRITICAL",
            "OTP Scam",
            "OTP / Verification, Urgency & Pressure, Threats & Legal Action, Financial & Payments, Suspicious Links",
            "2026-08-06 23:34:49"
        ),
        (
            "URGENT! Your HDFC Bank account will be blocked today due to pending KYC. Click link http://bit.ly/bank-kyc and share your OTP immediately.",
            "",
            "scam",
            0.991737,
            100,
            "CRITICAL",
            "OTP Scam",
            "OTP / Verification, Urgency & Pressure, Threats & Legal Action, Financial & Payments, Suspicious Links",
            "2026-08-06 23:24:27"
        ),
        (
            "live_recording.wav",
            "Hello Sir, I am speaking with SBI Band. Your ITM is going to be a short term. So, please come to your mobile phone and share your TPP.",
            "scam",
            0.805635,
            45,
            "MEDIUM",
            "Safe / Unknown Scam",
            "Banking Verification",
            "2026-08-06 23:20:33"
        ),
        (
            "c47459bfefe763f399de968edd245eb1.wav",
            "Hello Sir, I am from the State Bank of India. Your ATM is going to be closed. On your behalf I have a auto pv.",
            "safe",
            0.657729,
            20,
            "LOW",
            "Bank Scam",
            "Financial & Payments",
            "2026-08-06 23:19:26"
        ),
        (
            "c47459bfefe763f399de968edd245eb1.wav",
            "Hello Sir, I am from the State Bank of India. Your ATM is going to be closed. On your behalf I have a auto pv.",
            "safe",
            0.657729,
            20,
            "LOW",
            "Bank Scam",
            "Financial & Payments",
            "2026-08-06 23:07:35"
        ),
        (
            "Audio Call Transcript: Good morning, this is Senior Inspector Sharma from CBI Crime Branch New Delhi. A parcel under your Aadhaar number containing illegal narcotics was seized at Mumbai Customs. You are placed under digital arrest.",
            "Good morning, this is Senior Inspector Sharma from CBI Crime Branch New Delhi. A parcel under your Aadhaar number containing illegal narcotics was seized at Mumbai Customs. You are placed under digital arrest.",
            "scam",
            0.965,
            88,
            "CRITICAL",
            "Digital Arrest & Police Extortion",
            "Legal Intimidation, Police Coercion, Law Enforcement Impersonation",
            "2026-10-21 14:15:00"
        ),
        (
            "Dear Consumer, your electricity power connection will be disconnected tonight at 9:30 PM due to unpaid monthly bill. Call our bill verification officer at 9876543210 immediately.",
            "",
            "scam",
            0.942,
            75,
            "HIGH",
            "Utility Disconnection Scam",
            "Urgent Deadline, Service Disconnection Threat, Fake Support Phone",
            "2026-10-21 16:30:00"
        ),
        (
            "Congratulations! You have won a cash prize of Rs 50,000 from KBC Lottery. Deposit Rs 1,000 processing fee to claim right now.",
            "",
            "scam",
            0.978,
            90,
            "CRITICAL",
            "Lottery Scam",
            "Advance Fee, Fake Prize, Urgent Action",
            "2026-10-20 14:06:21"
        ),
        (
            "Hey! The team meeting has been rescheduled to 4 PM in the conference room. Please bring your project presentation slides.",
            "",
            "safe",
            0.994,
            2,
            "LOW",
            "Legitimate Personal Communication",
            "Normal Conversational Pattern",
            "2026-10-21 18:00:00"
        )
    ]
    try:
        cur = conn.cursor()
        if conn_type == "sqlite":
            cur.executemany("""
                INSERT INTO analysis_history (
                    input_text, transcript, prediction, confidence, risk_score, risk_level, scam_type, indicators, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, demo_records)
        else:
            cur.executemany("""
                INSERT INTO analysis_history (
                    input_text, transcript, prediction, confidence, risk_score, risk_level, scam_type, indicators, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
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
                input_text TEXT NOT NULL,
                transcript TEXT,
                prediction TEXT NOT NULL,
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
        return True, "Database synchronized successfully (SQLite engine active)."
    except Exception as e:
        return False, f"Database init error: {e}"

def init_db():
    cfg = get_config()
    if not should_try_mysql(cfg):
        return init_sqlite()

    try:
        conn = mysql.connector.connect(
            host=cfg["host"], port=cfg["port"],
            user=cfg["user"], password=cfg["password"],
            connection_timeout=2
        )
        cur = conn.cursor()
        cur.execute(f"CREATE DATABASE IF NOT EXISTS `{cfg['database']}`")
        cur.close()
        conn.close()

        conn = mysql.connector.connect(**cfg, connection_timeout=2)
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
    
    # Try MySQL if applicable
    if should_try_mysql(cfg):
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
        init_sqlite()
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
    # Try MySQL if applicable
    if should_try_mysql(cfg):
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
        init_sqlite()
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
