import sqlite3
import random
from datetime import datetime, timedelta


first_names = ["Amit", "Rahul", "Priya", "Sneha", "Karan", "Neha", "Rohit", "Anjali", "Vikas", "Pooja"]
last_names = ["Sharma", "Patil", "Verma", "Reddy", "Gupta", "Joshi", "Kumar", "Singh"]
cities = ["Pune", "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Nagpur", "Ahmedabad", "Jaipur"]

specializations = ["Dermatology", "Cardiology", "Orthopedics", "General", "Pediatrics"]

appointment_statuses = ["Scheduled", "Completed", "Cancelled", "No-Show"]
invoice_statuses = ["Paid", "Pending", "Overdue"]


def random_date_within_last_year():
    days_ago = random.randint(0, 365)
    return (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d %H:%M:%S")

def random_dob():
    years_ago = random.randint(18, 80)
    return (datetime.now() - timedelta(days=years_ago * 365)).strftime("%Y-%m-%d")

def random_name():
    return random.choice(first_names), random.choice(last_names)

def random_phone():
    return str(random.randint(7000000000, 9999999999)) if random.random() > 0.2 else None

def random_email(first, last):
    return f"{first.lower()}.{last.lower()}@gmail.com" if random.random() > 0.3 else None

def setup_database():
    conn = sqlite3.connect("clinic.db")
    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = ON;")

    cursor.executescript("""
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

    CREATE TABLE IF NOT EXISTS doctors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        specialization TEXT,
        department TEXT,
        phone TEXT
    );

    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        doctor_id INTEGER,
        appointment_date DATETIME,
        status TEXT,
        notes TEXT,
        FOREIGN KEY (patient_id) REFERENCES patients(id),
        FOREIGN KEY (doctor_id) REFERENCES doctors(id)
    );

    CREATE TABLE IF NOT EXISTS treatments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        appointment_id INTEGER,
        treatment_name TEXT,
        cost REAL,
        duration_minutes INTEGER,
        FOREIGN KEY (appointment_id) REFERENCES appointments(id)
    );

    CREATE TABLE IF NOT EXISTS invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        invoice_date DATE,
        total_amount REAL,
        paid_amount REAL,
        status TEXT,
        FOREIGN KEY (patient_id) REFERENCES patients(id)
    );
    """)

    doctor_ids = []
    for i in range(15):
        name = f"Dr. {random.choice(first_names)} {random.choice(last_names)}"
        spec = specializations[i % len(specializations)]
        dept = spec + " Dept"
        phone = random_phone()

        cursor.execute("""
        INSERT INTO doctors (name, specialization, department, phone)
        VALUES (?, ?, ?, ?)
        """, (name, spec, dept, phone))

        doctor_ids.append(cursor.lastrowid)

    patient_ids = []
    for _ in range(200):
        first, last = random_name()
        email = random_email(first, last)
        phone = random_phone()

        cursor.execute("""
        INSERT INTO patients (first_name, last_name, email, phone, date_of_birth, gender, city, registered_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            first,
            last,
            email,
            phone,
            random_dob(),
            random.choice(["M", "F"]),
            random.choice(cities),
            random_date_within_last_year().split()[0]
        ))

        patient_ids.append(cursor.lastrowid)

    appointment_ids = []
    for _ in range(500):
        patient_id = random.choice(patient_ids)
        doctor_id = random.choice(doctor_ids)

        status = random.choices(
            appointment_statuses,
            weights=[0.3, 0.4, 0.2, 0.1]
        )[0]

        notes = "Follow-up required" if random.random() > 0.7 else None

        cursor.execute("""
        INSERT INTO appointments (patient_id, doctor_id, appointment_date, status, notes)
        VALUES (?, ?, ?, ?, ?)
        """, (
            patient_id,
            doctor_id,
            random_date_within_last_year(),
            status,
            notes
        ))

        appointment_ids.append((cursor.lastrowid, status))

    completed_appointments = [a[0] for a in appointment_ids if a[1] == "Completed"]

    for appt_id in random.sample(completed_appointments, min(350, len(completed_appointments))):
        cursor.execute("""
        INSERT INTO treatments (appointment_id, treatment_name, cost, duration_minutes)
        VALUES (?, ?, ?, ?)
        """, (
            appt_id,
            random.choice(["Consultation", "X-Ray", "Therapy", "Surgery", "Medication"]),
            round(random.uniform(50, 5000), 2),
            random.randint(10, 120)
        ))

    for _ in range(300):
        patient_id = random.choice(patient_ids)
        total = round(random.uniform(100, 10000), 2)
        paid = total if random.random() > 0.4 else round(random.uniform(0, total), 2)

        status = "Paid" if paid == total else random.choice(["Pending", "Overdue"])

        cursor.execute("""
        INSERT INTO invoices (patient_id, invoice_date, total_amount, paid_amount, status)
        VALUES (?, ?, ?, ?, ?)
        """, (
            patient_id,
            random_date_within_last_year().split()[0],
            total,
            paid,
            status
        ))

    conn.commit()
    conn.close()

    print("Database created successfully!")
    print(f"Created 200 patients, 15 doctors, 500 appointments, 350 treatments, 300 invoices.")

if __name__ == "__main__":
    setup_database()