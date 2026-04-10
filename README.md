# Setup & usage documentation

# NL2SQL Chatbot using Vanna AI 2.0

## Overview

This project is a simple Natural Language to SQL (NL2SQL) system built using Vanna AI 2.0 and FastAPI.

The goal was to create a backend service where a user can ask questions in plain English and get answers from a database without writing SQL manually.

For example:

- Input: "Top 5 patients by spending"
- Output: SQL query + results from the database

The system generates SQL using an LLM, validates it for safety, executes it on a SQLite database, and returns structured results.

---

## Tech Stack

- Python 3.10+
- FastAPI
- Vanna AI 2.0
- SQLite
- Groq Console

---

## Project Structure


project/
├── setup_database.py
├── seed_memory.py
├── vanna_setup.py
├── main.py
├── requirements.txt
├── clinic.db
├── RESULTS.md
└── README.md


---

## Setup Instructions

### 1. Clone the repository


git clone <https://github.com/Sudu-hub/vanna-ai.git>
cd project


---

### 2. Create and activate virtual environment


python -m venv myenv
myenv\Scripts\activate


---

### 3. Install dependencies


pip install -r requirements.txt


---

### 4. Add API Key

Create a `.env` file in the root directory:


GROQ_API_KEY=your_api_key_here


---
# SQLite lock happen 
SQLite allows only one writer connection at a time

## Database Setup

Run the following script to create the SQLite database and populate it with dummy data:


python setup_database.py


This will create:
- Patients
- Doctors
- Appointments
- Treatments
- Invoices

The data is randomly generated but tries to simulate a realistic clinic system.

---

## Seeding Agent Memory

To improve SQL generation, I preloaded some example question-SQL pairs into the agent memory.

Run:


python seed_memory.py


This helps the agent generate better queries, especially for joins and aggregations.

---

## Running the API

Start the FastAPI server:


uvicorn main:app --port 8000


Once running, you can test the API using Postman or curl.

---

## API Endpoints

### POST `/chat`

**Request:**


{
"question": "How many patients do we have?"
}


**Response:**


{
"message": "Query executed successfully",
"sql_query": "SELECT COUNT(id) FROM patients",
"columns": ["COUNT(id)"],
"rows": [[400]],
"row_count": 1
}


---

### GET `/health`


{
"status": "ok",
"agent": "ready"
}


---

## How It Works (High Level)

1. User sends a question
2. FastAPI receives the request
3. Vanna agent generates SQL using Gemini
4. SQL is validated (only SELECT allowed, no dangerous keywords)
5. Query is executed on SQLite
6. Results are returned to the user

---

## SQL Validation

Before executing any query, I added a validation layer to ensure safety:

- Only SELECT queries are allowed
- Blocks keywords like INSERT, UPDATE, DELETE, DROP, etc.
- Prevents access to system tables like `sqlite_master`
- Disallows multiple SQL statements

---

## Error Handling

Handled a few common failure cases:

- If SQL is not generated → return error
- If query fails → catch DB error
- If no data found → return a friendly message

---

## Test Results

I tested the system with 20 different questions covering:

- Aggregations
- Joins
- Filters
- Time-based queries

Most queries worked correctly.

Some minor issues:
- Status values sometimes mismatched (e.g., "unpaid" vs "pending/overdue")
- A few queries could be optimized further

Detailed results are available in `RESULTS.md`.

---

## What I Learned

- Vanna 2.0 works very differently from 0.x (agent-based vs training-based)
- Prompt design plays a big role in SQL quality
- LLMs can generate valid SQL, but validation is necessary
- Memory seeding improves performance significantly

---

## Limitations

- SQL correctness depends on the prompt and memory
- Some queries may not be optimal
- No frontend (API only)

---

## Future Improvements

- Add chart generation (Plotly)
- Improve prompt engineering
- Add caching for repeated queries
- Add authentication and rate limiting

---

## LLM Provider Used

Groq Console (Free Tier)	https://console.groq.com

---

## Author

Sudarshan Sahane