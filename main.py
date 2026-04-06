from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
import sqlite3
from datetime import date

app = FastAPI(title="Skincare Routine API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    conn = sqlite3.connect('skincare_app.db')
    conn.row_factory = sqlite3.Row
    return conn

class ScheduleItem(BaseModel):
    product_name: str
    days: List[int]

@app.get("/")
def serve_frontend():
    return FileResponse("index.html")

@app.post("/schedule/update")
def update_schedule(items: List[ScheduleItem]):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Schedule")
    cursor.execute("UPDATE Cycle_State SET current_day_number = 1, last_checked_date = NULL WHERE id = 1")
    for item in items:
        for day in item.days:
            cursor.execute("INSERT INTO Schedule (product_name, day_number) VALUES (?, ?)", 
                           (item.product_name, day))
    cursor.execute("INSERT INTO Command_History (action_description) VALUES ('Uploaded new custom schedule.')")
    conn.commit()
    conn.close()
    return {"message": "New schedule saved successfully!"}

@app.get("/routine/today")
def get_today_routine():
    conn = get_db()
    cursor = conn.cursor()
    today_date = date.today().isoformat()
    cursor.execute("SELECT current_day_number, last_checked_date FROM Cycle_State WHERE id = 1")
    state = cursor.fetchone()
    current_day = state['current_day_number']
    last_checked = state['last_checked_date']
    
    if last_checked != today_date:
        if last_checked is not None:
            current_day += 1
        cursor.execute("SELECT MAX(day_number) as max_day FROM Schedule")
        max_day_row = cursor.fetchone()
        max_day = max_day_row['max_day'] if max_day_row['max_day'] else 1
        if current_day > max_day:
            current_day = 1
        cursor.execute("UPDATE Cycle_State SET current_day_number = ?, last_checked_date = ? WHERE id = 1", 
                       (current_day, today_date))
    
    cursor.execute("SELECT product_name FROM Schedule WHERE day_number = ?", (current_day,))
    products = [row['product_name'] for row in cursor.fetchall()]
    cursor.execute("INSERT INTO Command_History (action_description) VALUES (?)", 
                   (f"Checked routine for Day {current_day}.",))
    conn.commit()
    conn.close()
    return {"day_number": current_day, "products_to_use": products}

@app.get("/history")
def get_history():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, action_description FROM Command_History ORDER BY timestamp DESC LIMIT 15")
    history = [{"time": row["timestamp"], "action": row["action_description"]} for row in cursor.fetchall()]
    conn.close()
    return {"history": history}
