import sqlite3

def setup_database():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    ''')
    #cursor.execute("INSERT INTO users (user_id, password) VALUES ('admin', 'admin')")
    conn.commit()
    conn.close()


if __name__ == "__main__":
    setup_database()
    
    
    
    
    