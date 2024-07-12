import sqlite3



def insert_user(user_id, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Check if the user already exists
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    if cursor.fetchone():
        print(f"User {user_id} already exists. Skipping insertion.")
    else:
        cursor.execute("INSERT INTO users (user_id, password) VALUES (?, ?)", (user_id, password))
        conn.commit()
        print(f"User {user_id} inserted successfully.")
    
    conn.close()

if __name__ == "__main__":
    insert_user('anwesha_s', 'password123')
    insert_user('as', '123')



