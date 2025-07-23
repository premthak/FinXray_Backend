import json
import re
from typing import Dict, Any

def process_mca_filing(file_content: bytes, filename: str) -> Dict[str, Any]:
    """
    Process MCA filing documents using OCR and extract key financial/compliance data
    Simplified version for Render deployment - removes opencv and pytesseract dependencies
    """
    try:
        # Placeholder OCR processing
        # In production, this would use cloud OCR services or simpler text extraction

        compliance_data = {
            "company_name": extract_company_name(filename),
            "registration_number": "U12345DL2020PTC123456",
            "financial_year": "2023-24",
            "revenue": 15000000,  # 1.5 CR
            "profit_loss": 2000000,  # 20L profit
            "assets": 25000000,  # 2.5 CR
            "liabilities": 18000000,  # 1.8 CR
            "compliance_score": 85,
            "red_flags": [],
            "director_changes": 0,
            "pending_legal_cases": 0,
            "gst_compliance": True,
            "income_tax_filed": True
        }

        # Check for red flags
        if compliance_data["profit_loss"] < 0:
            compliance_data["red_flags"].append("Company showing losses")

        if compliance_data["liabilities"] > compliance_data["assets"]:
            compliance_data["red_flags"].append("Liabilities exceed assets")

        return compliance_data

    except Exception as e:
        return {"error": f"OCR processing failed: {str(e)}"}

def extract_company_name(filename: str) -> str:
    """Extract company name from filename"""
    # Remove file extension and clean up
    name = filename.split('.')[0]
    name = re.sub(r'[_-]', ' ', name)
    return name.title()

def validate_financial_data(data: Dict[str, Any]) -> bool:
    """Validate extracted financial data for consistency"""
    required_fields = ["revenue", "profit_loss", "assets", "liabilities"]
    return all(field in data for field in required_fields)
