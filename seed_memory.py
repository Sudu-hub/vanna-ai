# Agent memory seeding with 15 Q&A pairs

import asyncio
from vanna.core.user import RequestContext
from vanna_setup import create_agent

# -----------------------------
# Seed Data (Q&A pairs)
# -----------------------------
SEED_QUERIES = [
    # Patients
    ("How many patients do we have?",
     "SELECT COUNT(*) AS total_patients FROM patients"),

    ("List all patients from Mumbai",
     "SELECT first_name, last_name FROM patients WHERE city = 'Mumbai'"),

    ("How many female patients?",
     "SELECT COUNT(*) FROM patients WHERE gender = 'F'"),

    # Doctors
    ("List all doctors and their specializations",
     "SELECT name, specialization FROM doctors"),

    ("Which doctor has the most appointments?",
     """
     SELECT d.name, COUNT(*) as total_appointments
     FROM appointments a
     JOIN doctors d ON a.doctor_id = d.id
     GROUP BY d.name
     ORDER BY total_appointments DESC
     LIMIT 1
     """
    ),

    # Appointments
    ("Show all appointments last month",
     """
     SELECT * FROM appointments
     WHERE appointment_date >= date('now','-1 month')
     """
    ),

    ("How many cancelled appointments?",
     "SELECT COUNT(*) FROM appointments WHERE status = 'Cancelled'"),

    ("Appointments by status",
     "SELECT status, COUNT(*) FROM appointments GROUP BY status"),

    # Financial
    ("What is total revenue?",
     "SELECT SUM(total_amount) FROM invoices"),

    ("Show unpaid invoices",
     "SELECT * FROM invoices WHERE status != 'Paid'"),

    ("Top 5 patients by spending",
     """
     SELECT p.first_name, p.last_name, SUM(i.total_amount) as total_spent
     FROM invoices i
     JOIN patients p ON i.patient_id = p.id
     GROUP BY p.id
     ORDER BY total_spent DESC
     LIMIT 5
     """
    ),

    # Treatments
    ("Average treatment cost",
     "SELECT AVG(cost) FROM treatments"),

    ("Average treatment cost by specialization",
     """
     SELECT d.specialization, AVG(t.cost)
     FROM treatments t
     JOIN appointments a ON t.appointment_id = a.id
     JOIN doctors d ON a.doctor_id = d.id
     GROUP BY d.specialization
     """
    ),

    # Time-based
    ("Monthly appointment count",
     """
     SELECT strftime('%Y-%m', appointment_date) as month, COUNT(*)
     FROM appointments
     GROUP BY month
     ORDER BY month
     """
    ),

    ("Which city has most patients?",
     """
     SELECT city, COUNT(*) as total
     FROM patients
     GROUP BY city
     ORDER BY total DESC
     LIMIT 1
     """
    )
]

# -----------------------------
# Seed Function
# -----------------------------
async def seed_memory():
    agent = await create_agent()
    request = RequestContext()

    for question, sql in SEED_QUERIES:
        print(f"Seeding: {question}")

        # Trick: Ask agent with forced SQL context
        async for _ in agent.send_message(
            request,
            f"Question: {question}\nSQL: {sql}\nThis SQL is correct."
        ):
            pass

    print("\n✅ Memory seeding completed!")

# -----------------------------
# Run
# -----------------------------
if __name__ == "__main__":
    asyncio.run(seed_memory())