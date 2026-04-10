import asyncio
import sqlite3
import re

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from vanna.core.user import RequestContext
from vanna_setup import create_agent

app = FastAPI()

agent = None


# -----------------------------
# Request Schema
# -----------------------------
class ChatRequest(BaseModel):
    question: str


# -----------------------------
# Startup Event
# -----------------------------
@app.on_event("startup")
async def startup_event():
    global agent
    agent = await create_agent()


# -----------------------------
# SQL Validation
# -----------------------------
def validate_sql(sql: str):
    sql_lower = sql.lower()

    if not sql_lower.strip().startswith("select"):
        raise HTTPException(status_code=400, detail="Only SELECT queries are allowed")

    if re.search(r"\b(insert|update|delete|drop|alter|exec|grant|revoke)\b", sql_lower):
        raise HTTPException(status_code=400, detail="Dangerous SQL detected")

    if "sqlite_master" in sql_lower:
        raise HTTPException(status_code=400, detail="System table access blocked")


# -----------------------------
# Extract SQL from LLM output
# -----------------------------
def extract_sql(text: str):
    code_block = re.search(r"```sql(.*?)```", text, re.IGNORECASE | re.DOTALL)
    if code_block:
        return code_block.group(1).strip()

    match = re.search(r"(SELECT .*?)(;|$)", text, re.IGNORECASE | re.DOTALL)
    return match.group(1).strip() if match else ""


# -----------------------------
# Clean SQL
# -----------------------------
def clean_sql(sql: str):
    return " ".join(sql.replace(";", "").split())


# -----------------------------
# Execute SQL
# -----------------------------
def execute_sql(sql: str):
    conn = sqlite3.connect("clinic.db")
    cursor = conn.cursor()

    cursor.execute(sql)
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]

    conn.close()

    return columns, rows


# -----------------------------
# Generate Chart (basic)
# -----------------------------
def generate_chart(columns, rows):
    if len(columns) < 2 or len(rows) == 0:
        return None, None

    return {
        "data": [
            {
                "x": [row[0] for row in rows],
                "y": [row[1] for row in rows],
                "type": "bar"
            }
        ],
        "layout": {
            "title": "Query Result"
        }
    }, "bar"


# -----------------------------
# Chat Endpoint
# -----------------------------
@app.post("/chat")
async def chat(request: ChatRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    try:
        vanna_request = RequestContext()

        # -------------------------
        # Schema-aware prompt
        # -------------------------
        enhanced_prompt = f"""
You are an expert SQL assistant working with a SQLite database.

DATABASE SCHEMA:

patients(id, first_name, last_name, email, phone, date_of_birth, gender, city, registered_date)
doctors(id, name, specialization, department, phone)
appointments(id, patient_id, doctor_id, appointment_date, status, notes)
treatments(id, appointment_id, treatment_name, cost, duration_minutes)
invoices(id, patient_id, invoice_date, total_amount, paid_amount, status)

RULES:
- Use ONLY these tables and columns
- Use correct joins
- Revenue = invoices.total_amount
- Return ONLY SQL query
- Do NOT explain

User Question:
{request.question}
"""

        # -------------------------
        # Call agent
        # -------------------------
        full_response = ""

        async for chunk in agent.send_message(vanna_request, enhanced_prompt):
            if hasattr(chunk, "simple_component") and chunk.simple_component:
                text = getattr(chunk.simple_component, "text", "")
                full_response += text

        # -------------------------
        # Extract SQL
        # -------------------------
        raw_sql = extract_sql(full_response)
        sql_query = clean_sql(raw_sql) if raw_sql else ""

        if not sql_query:
            return {
                "message": "Failed to generate SQL",
                "sql_query": ""
            }

        # -------------------------
        # Validate SQL
        # -------------------------
        validate_sql(sql_query)

        # -------------------------
        # Execute SQL
        # -------------------------
        columns, rows = execute_sql(sql_query)

        # -------------------------
        # Chart
        # -------------------------
        chart, chart_type = generate_chart(columns, rows)

        # -------------------------
        # Response
        # -------------------------
        return {
            "message": "Query executed successfully",
            "sql_query": sql_query,
            "columns": columns,
            "rows": rows,
            "row_count": len(rows),
            "chart": chart,
            "chart_type": chart_type
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------
# Health Check
# -----------------------------
@app.get("/health")
async def health():
    return {
        "status": "ok",
        "agent": "ready",
        "database": "connected"
    }