from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import sqlite3
import os

app = FastAPI()
templates = Jinja2Templates(directory="templates")

DB_PATH = "payments.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            amount REAL NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()

def get_all_payments():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT id, name, amount, created_at FROM payments ORDER BY id DESC").fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1], "amount": r[2], "created_at": r[3]} for r in rows]

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    payments = get_all_payments()
    return templates.TemplateResponse("index.html", {"request": request, "payments": payments})

@app.post("/add")
async def add_payment(name: str = Form(...), amount: float = Form(...)):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO payments (name, amount) VALUES (?, ?)", (name, amount))
    conn.commit()
    conn.close()
    return RedirectResponse("/", status_code=303)

@app.post("/delete/{payment_id}")
async def delete_payment(payment_id: int):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM payments WHERE id = ?", (payment_id,))
    conn.commit()
    conn.close()
    return RedirectResponse("/", status_code=303)
