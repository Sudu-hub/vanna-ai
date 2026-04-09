import sqlite3

def create_database():

    conn = sqlite3.connect("clinic.db")
    cursor = conn.cursor()


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        date_of_birth DATE,
        gender TEXT,
        city TEXT,
        registered_date DATE
    );
    """)

    conn.commit()
    conn.close()

    print("database created successfully")

if __name__ == "__main__":
    create_database()