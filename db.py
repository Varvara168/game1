import sqlite3
from config import BASE_DIR


def get_value():
    conn = sqlite3.connect(BASE_DIR / "bd" / "LVL_NUM.db")
    cursor = conn.cursor()
    cursor.execute("SELECT Number FROM LVL")
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None
