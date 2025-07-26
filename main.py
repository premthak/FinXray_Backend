from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
import uvicorn
import os
import json
from datetime import datetime
import asyncio
import aiofiles

# Import our modules
from startup_data_fetcher import StartupDataFetcher
from ocr import process_mca_filing
from risk_model import calculate_risk_score
from email_notifications import send_risk_alert
from company_enrichment import enrich_company
from dashboard_helper import DashboardDataTransformer
app = FastAPI(
    title="FinXray Backend",
    description="AI-powered startup risk analysis platform",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://fin-xray-front.vercel.app"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Pydantic models
class AnalysisResponse(BaseModel):
    startup_name: str
    risk_score: float
    risk_category: str
    fraud_risk: float
    compliance_risk: float
    traction_risk: float
    founder_risk: float
    red_flags: List[str]
    email_sent: bool
    analysis_id: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class SubscriptionUpgrade(BaseModel):
    user_email: EmailStr
    plan: str
    amount: float

# Health check endpoint
@app.get("/")
async def health_check():
    return {
        "status": "healthy", 
        "service": "FinXray Backend",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

# Simple startup analysis endpoint
@app.post("/analyze-startup")
async def analyze_startup(company_name: str, domain: str):
    fetcher = StartupDataFetcher()
    data = await fetcher.fetch_startup_profile(company_name, domain)
    return data

# File upload and analysis endpoint
@app.post("/api/upload/analyze", response_model=AnalysisResponse)
async def analyze_startup_document(
    file: UploadFile = File(...),
    user_email: Optional[str] = None
):
    """
    Upload and analyze startup documents (MCA filings, pitch decks, etc.)
    Returns comprehensive risk analysis with AI-powered scoring
    """
    try:
        # Validate file type
        allowed_extensions = [".pdf", ".ppt", ".pptx", ".doc", ".docx"]
        file_extension = os.path.splitext(file.filename)[1].lower()

        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"File type {file_extension} not supported. Allowed: {allowed_extensions}"
            )

        # Read file content
        file_content = await file.read()

        # Process with OCR (extract MCA data, financial info)
        ocr_data = process_mca_filing(file_content, file.filename)

        if "error" in ocr_data:
            raise HTTPException(status_code=500, detail=ocr_data["error"])

        # Calculate comprehensive risk score using AI model
        risk_analysis = calculate_risk_score(ocr_data)

        # Generate analysis ID
        analysis_id = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Prepare response
        response = AnalysisResponse(
            startup_name=ocr_data.get("company_name", "Unknown Company"),
            risk_score=risk_analysis["overall_score"],
            risk_category=risk_analysis["risk_category"],
            fraud_risk=risk_analysis["fraud_risk"],
            compliance_risk=risk_analysis["compliance_risk"],
            traction_risk=risk_analysis["traction_risk"],
            founder_risk=risk_analysis["founder_risk"],
            red_flags=risk_analysis["red_flags"],
            email_sent=False,
            analysis_id=analysis_id
        )

        # Send email alert if high risk detected
        if risk_analysis["overall_score"] > 70 and user_email:
            try:
                email_sent = await send_risk_alert(
                    user_email, 
                    ocr_data.get("company_name", "Unknown Company"),
                    risk_analysis
                )
                response.email_sent = email_sent
            except Exception as email_error:
                print(f"Email sending failed: {email_error}")

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

# User authentication
@app.post("/api/auth/login")
async def login_user(credentials: UserLogin):
    """
    Authenticate user login
    """
    # Placeholder authentication - replace with real auth logic
    if credentials.email and credentials.password:
        return {
            "access_token": "dummy_token_12345",
            "token_type": "bearer",
            "user_email": credentials.email,
            "subscription_status": "free"  # or "premium"
        }
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

# Subscription management
@app.post("/api/subscription/upgrade")
async def upgrade_subscription(upgrade_data: SubscriptionUpgrade):
    """
    Handle subscription upgrades (â‚¹25K/month premium plan)
    """
    # Placeholder subscription logic - integrate with Razorpay/Stripe
    return {
        "message": "Subscription upgraded successfully",
        "user_email": upgrade_data.user_email,
        "plan": upgrade_data.plan,
        "amount": upgrade_data.amount,
        "status": "active",
        "next_billing_date": "2024-02-23"
    }

# User watchlist
@app.get("/api/watchlist/{user_email}")
async def get_user_watchlist(user_email: str):
    """
    Get user's saved startup analyses
    """
    # Placeholder - replace with database queries
    return {
        "user_email": user_email,
        "watchlist": [
            {
                "startup_name": "TechCorp Solutions",
                "risk_score": 25.5,
                "analysis_date": "2024-01-15",
                "status": "low_risk"
            },
            {
                "startup_name": "Innovation Labs",
                "risk_score": 78.2,
                "analysis_date": "2024-01-14", 
                "status": "high_risk"
            }
        ]
    }

# Get API documentation
@app.get("/api/docs")
async def get_api_info():
    """
    API information and usage statistics
    """
    return {
        "api_name": "FinXray Backend API",
        "version": "1.0.0",
        "endpoints": {
            "analyze": "/api/upload/analyze",
            "login": "/api/auth/login", 
            "upgrade": "/api/subscription/upgrade",
            "watchlist": "/api/watchlist/{user_email}"
        },
        "features": [
            "AI risk scoring",
            "MCA filing analysis", 
            "Email alerts",
            "Subscription management"
        ]
    }

# Company search endpoint (no file upload needed)
@app.get("/api/search/{company_name}")
async def search_company(company_name: str):
    """
    Search for company by name and return enriched data with risk analysis
    """
    try:
        # Get enriched data from external APIs
        enriched_data = await enrich_company(company_name)
        
        if not enriched_data.get("found_data", False):
            raise HTTPException(status_code=404, detail=f"No data found for company: {company_name}")
        
        # Calculate risk score using enriched data
        risk_analysis = calculate_risk_score(enriched_data)
        
        # Send alert if high risk
        if risk_analysis.get("overall", 0) >= 8:
            await send_risk_alert(
                company_name, 
                risk_analysis.get("overall", 0),
                risk_analysis.get("red_flags", [])
            )
        
        return {
            "startup_name": company_name,
            "risk_score": risk_analysis.get("overall", 0),
            "risk_category": risk_analysis.get("risk_category", "UNKNOWN"),
            "fraud_risk": risk_analysis.get("fraud", 0),
            "compliance_risk": risk_analysis.get("compliance", 0),
            "traction_risk": risk_analysis.get("traction", 0),
            "founder_risk": risk_analysis.get("founder", 0),
            "red_flags": risk_analysis.get("red_flags", []),
            "email_sent": risk_analysis.get("overall", 0) >= 8,
            "analysis_id": f"search_{company_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "data_sources": ["clearbit", "opencorporates", "crunchbase"],
            "enriched_data": enriched_data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing company: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

import random

@app.post("/api/upload/dashboard", response_model=dict)
async def analyze_startup_dashboard(
    file: UploadFile = File(...),
    user_email: Optional[str] = None
):
    """
    Enhanced dashboard endpoint that returns investor-grade analysis
    """
    try:
        # Process file using existing OCR logic
        file_content = await file.read()
        ocr_data = process_mca_filing(file_content, file.filename)

        if "error" in ocr_data:
            raise HTTPException(status_code=500, detail=ocr_data["error"])

        # Get risk analysis
        risk_analysis = calculate_risk_score(ocr_data)

        transformer = DashboardDataTransformer()
        dashboard_data = transformer.transform_to_dashboard_format(
            raw_data=ocr_data,
            company_name=ocr_data.get("company_name", "Unknown Company"),
            domain=ocr_data.get("industry", "Technology")
        )

        # Add comprehensive data for charts and tables
        dashboard_data.update({
            "funding_history": generate_funding_history(ocr_data),
            "timeline_data": generate_timeline_data(ocr_data),
            "market_analysis": generate_market_analysis(ocr_data),
            "competitor_analysis": generate_competitor_data(ocr_data),
            "executive_summary": generate_executive_summary(ocr_data, risk_analysis)
        })

        return dashboard_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard analysis failed: {str(e)}")

def generate_funding_history(ocr_data):
    """Generate mock funding history for dashboard"""
    return [
        {"round": "Seed", "amount": 500000, "date": "2022-03-15", "lead": "Angel Investors", "valuation": 2500000},
        {"round": "Series A", "amount": 3000000, "date": "2023-01-20", "lead": "Venture Capital XYZ", "valuation": 15000000},
        {"round": "Series B", "amount": 8000000, "date": "2024-06-10", "lead": "Growth Partners", "valuation": 40000000}
    ]

def generate_timeline_data(ocr_data):
    """Generate timeline data for charts"""
    return {
        "months": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        "revenue": [45000, 52000, 48000, 61000, 73000, 67000, 81000, 89000, 95000, 102000, 118000, 125000],
        "burn_rate": [75000, 78000, 72000, 80000, 85000, 82000, 88000, 90000, 87000, 92000, 95000, 98000],
        "users": [1200, 1450, 1380, 1680, 1950, 1820, 2100, 2350, 2480, 2690, 2880, 3120]
    }

def generate_market_analysis(ocr_data):
    """Generate market analysis data"""
    return {
        "tam": 50000000000,  # $50B
        "sam": 5000000000,   # $5B
        "som": 500000000,    # $500M
        "growth_rate": 15.5,
        "market_trends": ["AI Integration", "Mobile-First", "API Economy", "Subscription Models"]
    }

def generate_competitor_data(ocr_data):
    """Generate competitor analysis"""
    return [
        {"name": "Competitor A", "funding": 25000000, "employees": 150, "market_share": 12.5},
        {"name": "Competitor B", "funding": 45000000, "employees": 280, "market_share": 18.2},
        {"name": "Competitor C", "funding": 12000000, "employees": 85, "market_share": 8.7}
    ]

def generate_executive_summary(ocr_data, risk_analysis):
    """Generate executive summary"""
    company_name = ocr_data.get("company_name", "Unknown Company")
    risk_level = risk_analysis.get("risk_category", "MEDIUM")

    return {
        "headline": f"{company_name} shows {'strong potential' if risk_level == 'LOW' else 'moderate risk' if risk_level == 'MEDIUM' else 'elevated concerns'} for investment",
        "key_points": [
            f"Overall risk score: {risk_analysis.get('overall_score', 0)}/100",
            f"Current runway: {random.randint(8, 24)} months",
            f"Market opportunity: ${random.randint(1, 10)}B+ TAM",
            f"Team experience: {'Strong' if risk_analysis.get('founder_risk', 5) < 5 else 'Moderate'}"
        ],
        "recommendation": "PROCEED WITH DUE DILIGENCE" if risk_level != "HIGH" else "HIGH RISK - ADDITIONAL REVIEW REQUIRED"
    }
