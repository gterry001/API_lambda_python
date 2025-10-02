# main.py
#from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
#from fastapi.middleware.cors import CORSMiddleware
from .logic import run_portfolio_analysis
#from mangum import Mangum
#from pathlib import Path
# app/main.py
import os
from datetime import date, datetime
from typing import Optional

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum


app = FastAPI(title="Portfolio Risk API")

# CORS abierto para pruebas
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/run_portfolio_analysis")
def run_analysis_endpoint():
    print("Analyzing..... /")
    result = run_portfolio_analysis()
    print("Analysis ended /")
    return {
        "results": result
    }
@app.get("/")
def root():
    print("Exexuting...")
    return {"message": "API is running"}
handler = Mangum(app)

# ---------- Helpers de serialización ----------
def _iso(x):
    return x.isoformat() if hasattr(x, "isoformat") else x

def df_to_records(df: pd.DataFrame):
    if df is None or df.empty:
        return []
    # Limpia NaN -> None y fechas -> str
    out = (
        df.copy()
        .astype(object)
        .where(pd.notnull(df), None)
        .applymap(_iso)
        .to_dict(orient="records")
    )
    return out

@app.get("/analysis")
def analysis(
    invested_capital: float = Query(5000.0, ge=0),
    total_vol: float = Query(0.5, ge=0)
):
    result = run_portfolio_analysis(invested_capital, total_vol)
    return result
@app.get("/ohlc/{coin}")
def ohlc(
    coin: str,
    start: Optional[str] = Query(None, description="YYYY-MM-DD"),
    end: Optional[str] = Query(None, description="YYYY-MM-DD"),
    limit: int = Query(3000, ge=1, le=10000),
):
    # Carga datos (puedes cachear en /tmp si quieres acelerar)
    portfolio, dfs = download_data()
    if coin not in dfs:
        raise HTTPException(status_code=404, detail="Coin not found")

    df = dfs[coin].copy()

    # Normaliza fechas si existen
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"]).dt.date

    # Filtros
    if start:
        start_d = datetime.strptime(start, "%Y-%m-%d").date()
        df = df[df["date"] >= start_d] if "date" in df.columns else df
    if end:
        end_d = datetime.strptime(end, "%Y-%m-%d").date()
        df = df[df["date"] <= end_d] if "date" in df.columns else df

    # Limita filas
    if len(df) > limit:
        df = df.tail(limit)

    return df_to_records(df)

@app.get("/dashboard-data")
def dashboard_data():
    return run_dashboard_data()

@app.get("/coins")
def coins():
    portfolio, dfs = download_data()
    # Preferimos del portfolio para “oficiales”:
    coin_list = sorted(pd.Series(portfolio["Coin"]).dropna().unique().tolist())
    return {"coins": coin_list}




