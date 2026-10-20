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
    return {
        "host": os.getenv("MYSQL_HOST", "localhost"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", ""),
        "database": os.getenv("MYSQL_DATABASE", "scamguard")
    }

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
            user=cfg["user"], password=cfg["password"]
        )
        cur = conn.cursor()
        cur.execute(f"CREATE DATABASE IF NOT EXISTS `{cfg['database']}`")
        cur.close()
        conn.close()

        conn = mysql.connector.connect(**cfg)
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
        cur.close()
        conn.close()
        return True, "MySQL database connected and synchronized successfully."
    except Error:
        # Fall back gracefully to SQLite if MySQL is unavailable or credentials differ
        return init_sqlite()

def save_analysis(message, prediction, risk_score, scam_type, indicators, transcript="", confidence=0.0, risk_level="LOW"):
    indicators_str = ", ".join(indicators) if isinstance(indicators, (list, tuple)) else str(indicators)
    cfg = get_config()
    
    # Try MySQL first
    try:
        conn = mysql.connector.connect(**cfg)
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
        conn = mysql.connector.connect(**cfg)
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
