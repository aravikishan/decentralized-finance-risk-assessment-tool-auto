
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List
from datetime import datetime
import sqlite3
import os

# Initialize FastAPI app
app = FastAPI()

# Setup templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Database setup
DATABASE_URL = "sqlite:///./test.db"

# Ensure the database and tables are created
if not os.path.exists("./test.db"):
    conn = sqlite3.connect("test.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS User (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Portfolio (
            portfolio_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            assets TEXT,
            FOREIGN KEY (user_id) REFERENCES User (user_id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS RiskAssessment (
            assessment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            portfolio_id INTEGER,
            risk_score REAL,
            timestamp DATETIME,
            FOREIGN KEY (portfolio_id) REFERENCES Portfolio (portfolio_id)
        )
    ''')
    # Insert seed data
    cursor.execute("INSERT INTO User (name, email) VALUES ('John Doe', 'john@example.com')")
    cursor.execute("INSERT INTO Portfolio (user_id, assets) VALUES (1, '[{"asset_id": 1, "type": "crypto", "amount": 100.0}]')")
    cursor.execute("INSERT INTO RiskAssessment (portfolio_id, risk_score, timestamp) VALUES (1, 0.5, ?)", (datetime.now(),))
    conn.commit()
    conn.close()

# Pydantic models
class User(BaseModel):
    user_id: int
    name: str
    email: str

class Asset(BaseModel):
    asset_id: int
    type: str
    amount: float

class Portfolio(BaseModel):
    portfolio_id: int
    user_id: int
    assets: List[Asset]

class RiskAssessment(BaseModel):
    assessment_id: int
    portfolio_id: int
    risk_score: float
    timestamp: datetime

# Routes
@app.get("/", response_class=HTMLResponse)
async def read_dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/portfolio", response_class=HTMLResponse)
async def manage_portfolio(request: Request):
    return templates.TemplateResponse("portfolio.html", {"request": request})

@app.get("/risk-analysis", response_class=HTMLResponse)
async def risk_analysis(request: Request):
    return templates.TemplateResponse("risk_analysis.html", {"request": request})

@app.get("/api-docs", response_class=HTMLResponse)
async def api_docs(request: Request):
    return templates.TemplateResponse("api_docs.html", {"request": request})

@app.get("/api/portfolios")
async def get_portfolios():
    conn = sqlite3.connect("test.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Portfolio")
    portfolios = cursor.fetchall()
    conn.close()
    return portfolios

@app.post("/api/portfolio")
async def create_portfolio(portfolio: Portfolio):
    conn = sqlite3.connect("test.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Portfolio (user_id, assets) VALUES (?, ?)", (portfolio.user_id, str(portfolio.assets)))
    conn.commit()
    conn.close()
    return {"message": "Portfolio created successfully"}

@app.get("/api/risk-score/{user_id}")
async def get_risk_score(user_id: int):
    conn = sqlite3.connect("test.db")
    cursor = conn.cursor()
    cursor.execute("SELECT risk_score FROM RiskAssessment WHERE portfolio_id = ?", (user_id,))
    risk_score = cursor.fetchone()
    conn.close()
    if risk_score:
        return {"risk_score": risk_score[0]}
    else:
        raise HTTPException(status_code=404, detail="Risk score not found")

@app.get("/api/historical-data/{user_id}")
async def get_historical_data(user_id: int):
    conn = sqlite3.connect("test.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM RiskAssessment WHERE portfolio_id = ?", (user_id,))
    data = cursor.fetchall()
    conn.close()
    return data
