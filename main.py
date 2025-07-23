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
from ocr import process_mca_filing
from risk_model import calculate_risk_score
from email_notifications import send_risk_alert

app = FastAPI(
    title="FinXray Backend",
    description="AI-powered startup risk analysis platform",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with your Vercel domain in production
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
    Handle subscription upgrades (₹25K/month premium plan)
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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
