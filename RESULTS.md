# Test results for 20 questions

1] How many patients do we have?
> {
  "message": "Query executed successfully",
  "sql_query": "SELECT COUNT(id) FROM patients",
  "columns": [
    "COUNT(id)"
  ],
  "rows": [
    [
      400
    ]
  ],
  "row_count": 1,
  "chart": null,
  "chart_type": null
}

2] List all doctors and their specializations
> "message": "Query executed successfully",
  "sql_query": "SELECT id, name, specialization FROM doctors",

3] Show me appointments for last month
> 
  "message": "Query executed successfully",
  "sql_query": "SELECT a.id, p.first_name, p.last_name, d.name, a.appointment_date, a.status FROM appointments a JOIN patients p ON a.patient_id = p.id JOIN doctors d ON a.doctor_id = d.id WHERE STRFTIME('%Y-%m', a.appointment_date) = STRFTIME('%Y-%m', DATE('now', '-1 month'))"

4] Which doctor has the most appointments?
> "message": "Query executed successfully",
  "sql_query": "SELECT D.name, COUNT(A.id) AS total_appointments FROM doctors D JOIN appointments A ON D.id = A.doctor_id GROUP BY D.name ORDER BY total_appointments DESC LIMIT 1"

5] What is the total revenue?
> "message": "Query executed successfully",
  "sql_query": "SELECT SUM(total_amount) AS total_revenue FROM invoices"

6] Show revenue by doctor
>"message": "Query executed successfully",
  "sql_query": "SELECT D.name, SUM(I.total_amount) AS revenue FROM invoices I JOIN patients P ON I.patient_id = P.id JOIN appointments A ON P.id = A.patient_id JOIN doctors D ON A.doctor_id = D.id GROUP BY D.name"

7]How many cancelled appointments last quarter?
> "message": "Query executed successfully",
  "sql_query": "SELECT COUNT(a.id) FROM appointments a WHERE a.status = 'cancelled' AND strftime('%Y', a.appointment_date) = strftime('%Y', 'now') AND CAST(strftime('%m', a.appointment_date) AS INT) IN (10, 11, 12)"

8] Top 5 patients by spending
> "message": "Query executed successfully",
  "sql_query": "SELECT p.first_name, p.last_name, SUM(i.total_amount) AS total_spent FROM patients p JOIN invoices i ON p.id = i.patient_id GROUP BY p.id, p.first_name, p.last_name ORDER BY total_spent DESC LIMIT 5"

9] Average treatment cost by specialization
> "message": "Query executed successfully",
  "sql_query": "SELECT D.specialization, AVG(T.cost) as average_treatment_cost FROM treatments T JOIN appointments A ON T.appointment_id = A.id JOIN doctors D ON A.doctor_id = D.id GROUP BY D.specialization"

10] Show monthly appointment count for the past 6 months
> "message": "Query executed successfully",
  "sql_query": "SELECT STRFTIME('%Y-%m', appointment_date) AS month, COUNT(*) AS appointment_count FROM appointments WHERE appointment_date >= DATE('now', '-6 month') GROUP BY STRFTIME('%Y-%m', appointment_date) ORDER BY month DESC"

11] Which city has the most patients?
> "message": "Query executed successfully",
  "sql_query": "SELECT city, COUNT(*) as patient_count FROM patients GROUP BY city ORDER BY patient_count DESC LIMIT 1"

12] List patients who visited more than 3 times
> "message": "Query executed successfully",
  "sql_query": "SELECT p.id, p.first_name, p.last_name, COUNT(a.id) AS visit_count FROM patients p JOIN appointments a ON p.id = a.patient_id GROUP BY p.id, p.first_name, p.last_name HAVING COUNT(a.id) > 3"

13] Show unpaid invoices
> "message": "Query executed successfully",
  "sql_query": "SELECT * FROM invoices WHERE paid_amount < total_amount AND status = 'unpaid'"

14] What percentage of appointments are no-shows?
> "message": "Query executed successfully",
  "sql_query": "SELECT (COUNT(CASE WHEN status = 'no-show' THEN 1 END) * 1.0 / COUNT(id)) * 100 FROM appointments"

15] Show the busiest day of the week for appointments
> "message": "Query executed successfully",
  "sql_query": "SELECT CASE WHEN STRFTIME('%w', appointment_date) = '0' THEN 'Sunday' WHEN STRFTIME('%w', appointment_date) = '1' THEN 'Monday' WHEN STRFTIME('%w', appointment_date) = '2' THEN 'Tuesday' WHEN STRFTIME('%w', appointment_date) = '3' THEN 'Wednesday' WHEN STRFTIME('%w', appointment_date) = '4' THEN 'Thursday' WHEN STRFTIME('%w', appointment_date) = '5' THEN 'Friday' WHEN STRFTIME('%w', appointment_date) = '6' THEN 'Saturday' END AS day_of_week, COUNT(*) as total_appointments FROM appointments GROUP BY STRFTIME('%w', appointment_date) ORDER BY total_appointments DESC LIMIT 1"

16] Revenue trend by month
> "message": "Query executed successfully",
  "sql_query": "SELECT STRFTIME('%Y-%m', invoice_date) AS month, SUM(total_amount) AS revenue FROM invoices GROUP BY STRFTIME('%Y-%m', invoice_date) ORDER BY month"

17] Average appointment duration by doctor
> "message": "Query executed successfully",
  "sql_query": "SELECT D.name, AVG(T.duration_minutes) AS average_appointment_duration FROM doctors D JOIN appointments A ON D.id = A.doctor_id JOIN treatments T ON A.id = T.appointment_id GROUP BY D.name"

18] List patients with overdue invoices
> "message": "Query executed successfully",
  "sql_query": "SELECT p.id, p.first_name, p.last_name, p.email, i.invoice_date, i.total_amount, i.paid_amount FROM patients p JOIN invoices i ON p.id = i.patient_id WHERE i.status = 'unpaid' AND i.invoice_date < DATE('now')"

19] Compare revenue between departments
> "message": "Query executed successfully",
  "sql_query": "SELECT D.department, SUM(I.total_amount) AS revenue FROM invoices I JOIN appointments A ON I.patient_id = A.patient_id JOIN doctors D ON A.doctor_id = D.id GROUP BY D.department",


20] Show patient registration trend by month
> "message": "Query executed successfully",
  "sql_query": "SELECT STRFTIME('%Y-%m', registered_date) AS registration_month, COUNT(id) AS number_of_patients FROM patients GROUP BY STRFTIME('%Y-%m', registered_date) ORDER BY registration_month"


# Evaluation Summary
    Total Questions: 20
    Passed: 17
    Failed: 3
    Accuracy: 85%


** Failed Cases Analysis
1. Incorrect JOIN Logic
    Seen in revenue-related queries
    Causes duplication or wrong aggregation

2. Hardcoded Time Filters
    Example: last quarter using fixed months
    Not dynamic → fails in real scenarios

3. Wrong Relationship Mapping
    Using patient_id instead of appointment_id
    Breaks data integrity