import sqlite3
import random
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()

DB_NAME = "clinic.db"

# -----------------------------
# Helper Functions
# -----------------------------
def random_date_within_last_year():
    today = datetime.now()
    past = today - timedelta(days=365)
    return fake.date_between(start_date=past, end_date=today)

def random_datetime_within_last_year():
    today = datetime.now()
    past = today - timedelta(days=365)
    return fake.date_time_between(start_date=past, end_date=today)

# -----------------------------
# Create Tables
# -----------------------------
def create_tables(conn):
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
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS doctors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        specialization TEXT,
        department TEXT,
        phone TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        doctor_id INTEGER,
        appointment_date DATETIME,
        status TEXT,
        notes TEXT,
        FOREIGN KEY(patient_id) REFERENCES patients(id),
        FOREIGN KEY(doctor_id) REFERENCES doctors(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS treatments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        appointment_id INTEGER,
        treatment_name TEXT,
        cost REAL,
        duration_minutes INTEGER,
        FOREIGN KEY(appointment_id) REFERENCES appointments(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        invoice_date DATE,
        total_amount REAL,
        paid_amount REAL,
        status TEXT,
        FOREIGN KEY(patient_id) REFERENCES patients(id)
    )
    """)

    conn.commit()

# -----------------------------
# Insert Data
# -----------------------------
def insert_data(conn):
    cursor = conn.cursor()

    # -------- Doctors --------
    specializations = ["Dermatology", "Cardiology", "Orthopedics", "General", "Pediatrics"]
    departments = ["Skin", "Heart", "Bones", "General Medicine", "Child Care"]

    doctor_ids = []
    for _ in range(15):
        name = fake.name()
        spec = random.choice(specializations)
        dept = random.choice(departments)
        phone = fake.phone_number()

        cursor.execute("""
            INSERT INTO doctors (name, specialization, department, phone)
            VALUES (?, ?, ?, ?)
        """, (name, spec, dept, phone))

        doctor_ids.append(cursor.lastrowid)

    # -------- Patients --------
    cities = ["Mumbai", "Pune", "Delhi", "Bangalore", "Chennai", "Hyderabad", "Kolkata", "Ahmedabad"]

    patient_ids = []
    for _ in range(200):
        first_name = fake.first_name()
        last_name = fake.last_name()

        email = fake.email() if random.random() > 0.2 else None
        phone = fake.phone_number() if random.random() > 0.2 else None

        dob = fake.date_of_birth(minimum_age=1, maximum_age=90)
        gender = random.choice(["M", "F"])
        city = random.choice(cities)
        reg_date = random_date_within_last_year()

        cursor.execute("""
            INSERT INTO patients 
            (first_name, last_name, email, phone, date_of_birth, gender, city, registered_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (first_name, last_name, email, phone, dob, gender, city, reg_date))

        patient_ids.append(cursor.lastrowid)

    # -------- Appointments --------
    statuses = ["Scheduled", "Completed", "Cancelled", "No-Show"]

    appointment_ids = []
    completed_appointments = []

    for _ in range(500):
        patient_id = random.choice(patient_ids)

        # skew distribution: some doctors busier
        doctor_id = random.choice(doctor_ids + doctor_ids[:5])

        appt_date = random_datetime_within_last_year()
        status = random.choices(
            statuses,
            weights=[0.2, 0.5, 0.2, 0.1]
        )[0]

        notes = fake.sentence() if random.random() > 0.3 else None

        cursor.execute("""
            INSERT INTO appointments 
            (patient_id, doctor_id, appointment_date, status, notes)
            VALUES (?, ?, ?, ?, ?)
        """, (patient_id, doctor_id, appt_date, status, notes))

        appt_id = cursor.lastrowid
        appointment_ids.append(appt_id)

        if status == "Completed":
            completed_appointments.append(appt_id)

    # -------- Treatments --------
    treatment_names = ["X-Ray", "Blood Test", "MRI Scan", "Physiotherapy", "Consultation"]

    for appt_id in random.sample(completed_appointments, min(350, len(completed_appointments))):
        cost = round(random.uniform(50, 5000), 2)
        duration = random.randint(10, 120)
        treatment = random.choice(treatment_names)

        cursor.execute("""
            INSERT INTO treatments 
            (appointment_id, treatment_name, cost, duration_minutes)
            VALUES (?, ?, ?, ?)
        """, (appt_id, treatment, cost, duration))

    # -------- Invoices --------
    for _ in range(300):
        patient_id = random.choice(patient_ids)
        invoice_date = random_date_within_last_year()

        total_amount = round(random.uniform(50, 5000), 2)

        status = random.choice(["Paid", "Pending", "Overdue"])

        if status == "Paid":
            paid_amount = total_amount
        elif status == "Pending":
            paid_amount = round(total_amount * random.uniform(0.3, 0.9), 2)
        else:
            paid_amount = 0

        cursor.execute("""
            INSERT INTO invoices 
            (patient_id, invoice_date, total_amount, paid_amount, status)
            VALUES (?, ?, ?, ?, ?)
        """, (patient_id, invoice_date, total_amount, paid_amount, status))

    conn.commit()

    return {
        "patients": len(patient_ids),
        "doctors": len(doctor_ids),
        "appointments": len(appointment_ids),
        "treatments": min(350, len(completed_appointments)),
        "invoices": 300
    }

# -----------------------------
# Main
# -----------------------------
def main():
    conn = sqlite3.connect(DB_NAME, timeout=10)

    try:
        create_tables(conn)
        summary = insert_data(conn)

    finally:
        conn.close()

    print(
        f"Created {summary['patients']} patients, "
        f"{summary['doctors']} doctors, "
        f"{summary['appointments']} appointments, "
        f"{summary['treatments']} treatments, "
        f"{summary['invoices']} invoices."
    )

if __name__ == "__main__":
    main()