from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import re

app = FastAPI()

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/analyze")
async def analyze_startup(
    file: UploadFile = File(...),
    industry: Optional[str] = "general"
):
    file_content = await file.read()
    text = file_content.decode("utf-8", errors="ignore")

    def extract_number(pattern):
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            num = match.group(2).replace(",", "")
            try:
                return float(num)
            except:
                return None
        return None

    results = {
        "revenue": extract_number(r"(revenue|income)[\s:₹$]*([\d,.]+)"),
        "expenses": extract_number(r"(expenses|cost)[\s:₹$]*([\d,.]+)"),
        "profit": extract_number(r"(profit|net income)[\s:₹$]*([\d,.]+)"),
        "valuation": extract_number(r"(valuation|worth)[\s:₹$]*([\d,.]+)"),
        "ai_kpi_score": 82,
        "financial_kpi_score": 76,
        "red_flags": [],
        "market_comparison": {}
    }

    if results["expenses"] and results["revenue"] and results["expenses"] > results["revenue"]:
        results["red_flags"].append("Expenses are higher than revenue.")
    if not results["valuation"]:
        results["red_flags"].append("No valuation data found.")

    # Sample market comparison logic
    industry_avg = {
        "general": {
            "profit_margin": 15,
            "valuation_range": (1_000_000, 10_000_000),
        }
    }
    if results["profit"] and results["revenue"]:
        actual_margin = (results["profit"] / results["revenue"]) * 100
        results["market_comparison"]["profit_margin_vs_industry"] = round(actual_margin - industry_avg[industry]["profit_margin"], 2)

    if results["valuation"]:
        min_val, max_val = industry_avg[industry]["valuation_range"]
        if results["valuation"] < min_val:
            results["market_comparison"]["valuation_flag"] = "Low valuation for this industry"
        elif results["valuation"] > max_val:
            results["market_comparison"]["valuation_flag"] = "High valuation for this industry"

    return {
        "success": True,
        "analysis": results
    }

