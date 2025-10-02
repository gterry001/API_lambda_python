# main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from .logic import run_portfolio_analysis
from mangum import Mangum
from pathlib import Path

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
        "results": result,
        "grafico_url": f"/static/{result['plot_file']}"
    }
@app.get("/")
def root():
    print("Exexuting...")
    return {"message": "API is running"}
handler = Mangum(app)








