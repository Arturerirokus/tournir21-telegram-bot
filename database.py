import sqlite3

def init_db():
    conn = sqlite3.connect('tournament.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS participants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            username TEXT,
            full_name TEXT,
            game TEXT,
            game_nickname TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_participant(user_id, username, full_name, game, game_nickname):
    conn = sqlite3.connect('tournament.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT OR IGNORE INTO participants (user_id, username, full_name, game, game_nickname)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, username, full_name, game, game_nickname))
        conn.commit()
        success = cursor.rowcount > 0
    except Exception:
        success = False
    finally:
        conn.close()
    return success

def get_participants():
    conn = sqlite3.connect('tournament.db')
    cursor = conn.cursor()
    cursor.execute('SELECT full_name, game, game_nickname FROM participants')
    rows = cursor.fetchall()
    conn.close()
    return rows