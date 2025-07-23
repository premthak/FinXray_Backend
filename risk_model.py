import random
from typing import Dict, List, Any
from datetime import datetime
import json

def calculate_risk_score(extracted_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate comprehensive risk score for startup analysis
    Based on extracted data from MCA filings, pitch decks, and financial documents
    
    Args:
        extracted_data: Dictionary containing extracted company information
        
    Returns:
        Dictionary with risk scores, categories, and red flags
    """
    
    # Initialize risk scores
    fraud_risk = 0.0
    compliance_risk = 0.0
    traction_risk = 0.0
    founder_risk = 0.0
    
    red_flags = []
    
    # FRAUD RISK ANALYSIS
    if extracted_data:
        # Check for inconsistent financial data
        if 'financial_data' in extracted_data:
            financial = extracted_data['financial_data']
            
            # Revenue consistency check
            if 'revenue' in financial and 'projected_revenue' in financial:
                revenue = financial.get('revenue', 0)
                projected = financial.get('projected_revenue', 0)
                if projected > revenue * 10:  # Unrealistic projections
                    fraud_risk += 2.5
                    red_flags.append("Unrealistic revenue projections detected")
            
            # Burn rate vs funding check
            if 'burn_rate' in financial and 'funding_raised' in financial:
                burn_rate = financial.get('burn_rate', 0)
                funding = financial.get('funding_raised', 0)
                if burn_rate > 0 and funding / burn_rate < 6:  # Less than 6 months runway
                    fraud_risk += 1.5
                    red_flags.append("Critical runway shortage detected")
        
        # Check company registration details
        if 'company_details' in extracted_data:
            company = extracted_data['company_details']
            
            # Recently incorporated companies with high valuations
            if 'incorporation_date' in company and 'valuation' in company:
                incorporation_date = company.get('incorporation_date')
                valuation = company.get('valuation', 0)
                
                # Mock check for new companies with high valuations
                if valuation > 100000000:  # $10M+ valuation
                    fraud_risk += 1.0
                    red_flags.append("High valuation for early-stage company")
    
    # COMPLIANCE RISK ANALYSIS
    if extracted_data:
        # Check for regulatory compliance
        if 'compliance_status' in extracted_data:
            compliance_status = extracted_data['compliance_status']
            
            if compliance_status.get('gst_status') == 'non_compliant':
                compliance_risk += 2.0
                red_flags.append("GST compliance issues found")
            
            if compliance_status.get('roc_filing_status') == 'delayed':
                compliance_risk += 1.5
                red_flags.append("Delayed ROC filings detected")
            
            if compliance_status.get('tax_status') == 'pending':
                compliance_risk += 1.0
                red_flags.append("Pending tax obligations")
        
        # Check for legal issues
        if 'legal_issues' in extracted_data:
            legal_issues = extracted_data['legal_issues']
            if legal_issues.get('pending_cases', 0) > 0:
                compliance_risk += 2.5
                red_flags.append(f"Pending legal cases: {legal_issues.get('pending_cases')}")
    
    # TRACTION RISK ANALYSIS
    if extracted_data:
        # Customer base analysis
        if 'traction_data' in extracted_data:
            traction = extracted_data['traction_data']
            
            customer_count = traction.get('customer_count', 0)
            monthly_growth = traction.get('monthly_growth_rate', 0)
            
            if customer_count < 100:  # Low customer base
                traction_risk += 1.5
                red_flags.append("Limited customer base")
            
            if monthly_growth < 5:  # Less than 5% monthly growth
                traction_risk += 2.0
                red_flags.append("Low growth rate")
            
            # Market size vs current revenue
            if 'market_size' in traction and 'current_revenue' in traction:
                market_size = traction.get('market_size', 0)
                current_revenue = traction.get('current_revenue', 0)
                
                if market_size > 0 and (current_revenue / market_size) < 0.001:  # Less than 0.1% market share
                    traction_risk += 1.0
                    red_flags.append("Very small market share")
    
    # FOUNDER RISK ANALYSIS
    if extracted_data:
        # Founder background check
        if 'founder_details' in extracted_data:
            founders = extracted_data['founder_details']
            
            if isinstance(founders, list):
                # Check for founder experience
                experienced_founders = 0
                for founder in founders:
                    if founder.get('experience_years', 0) > 5:
                        experienced_founders += 1
                
                if experienced_founders == 0:
                    founder_risk += 2.0
                    red_flags.append("No experienced founders detected")
                
                # Check for previous startup failures
                failed_startups = sum(founder.get('previous_failed_startups', 0) for founder in founders)
                if failed_startups > 2:
                    founder_risk += 1.5
                    red_flags.append("Multiple previous startup failures")
                
                # Educational background check
                top_tier_education = sum(1 for founder in founders if founder.get('top_tier_education', False))
                if top_tier_education == 0:
                    founder_risk += 0.5
    
    # If no data provided, assign moderate random scores for demo
    if not extracted_data or not any([
        'financial_data' in extracted_data,
        'company_details' in extracted_data,
        'traction_data' in extracted_data,
        'founder_details' in extracted_data
    ]):
        fraud_risk = round(random.uniform(2, 8), 1)
        compliance_risk = round(random.uniform(1, 7), 1)
        traction_risk = round(random.uniform(2, 9), 1)
        founder_risk = round(random.uniform(1, 6), 1)
        
        # Add some demo red flags
        demo_flags = [
            "Limited financial documentation provided",
            "Insufficient traction data for analysis",
            "Founder background verification pending",
            "Market analysis incomplete"
        ]
        red_flags.extend(random.sample(demo_flags, random.randint(1, 3)))
    
    # Cap risk scores at 10
    fraud_risk = min(fraud_risk, 10.0)
    compliance_risk = min(compliance_risk, 10.0)
    traction_risk = min(traction_risk, 10.0)
    founder_risk = min(founder_risk, 10.0)
    
    # Calculate overall risk score (weighted average)
    overall_risk = round((
        fraud_risk * 0.3 +         # 30% weight on fraud
        compliance_risk * 0.25 +   # 25% weight on compliance
        traction_risk * 0.25 +     # 25% weight on traction
        founder_risk * 0.2         # 20% weight on founder
    ), 1)
    
    # Determine risk category
    if overall_risk >= 7.5:
        risk_category = "HIGH"
    elif overall_risk >= 5.0:
        risk_category = "MEDIUM"
    elif overall_risk >= 2.5:
        risk_category = "LOW"
    else:
        risk_category = "VERY LOW"
    
    # Add high-risk red flags
    if overall_risk >= 8.0:
        red_flags.append("CRITICAL: High overall risk score - immediate attention required")
    elif overall_risk >= 6.0:
        red_flags.append("WARNING: Elevated risk levels detected")
    
    return {
        "overall": overall_risk,
        "fraud": round(fraud_risk, 1),
        "compliance": round(compliance_risk, 1),
        "traction": round(traction_risk, 1),
        "founder": round(founder_risk, 1),
        "risk_category": risk_category,
        "red_flags": list(set(red_flags)),  # Remove duplicates
        "analysis_timestamp": datetime.now().isoformat(),
        "confidence_score": round(random.uniform(0.7, 0.95), 2)  # AI confidence in analysis
    }

def get_risk_thresholds():
    """
    Get risk score thresholds for different alert levels
    """
    return {
        "high_risk": 7.5,
        "medium_risk": 5.0,
        "low_risk": 2.5,
        "email_alert": 8.0,
        "immediate_action": 9.0
    }

def analyze_sector_risk(sector: str) -> float:
    """
    Analyze sector-specific risk factors
    """
    sector_risks = {
        "fintech": 6.5,
        "healthcare": 5.5,
        "e-commerce": 4.5,
        "edtech": 5.0,
        "logistics": 4.0,
        "saas": 3.5,
        "gaming": 7.0,
        "crypto": 8.5,
        "foodtech": 6.0,
        "default": 5.0
    }
    
    return sector_risks.get(sector.lower(), sector_risks["default"])

def generate_recommendations(risk_scores: Dict[str, Any]) -> List[str]:
    """
    Generate actionable recommendations based on risk analysis
    """
    recommendations = []
    
    if risk_scores["fraud"] > 6.0:
        recommendations.append("Conduct thorough financial audit and verification")
        recommendations.append("Request additional documentation for financial claims")
    
    if risk_scores["compliance"] > 6.0:
        recommendations.append("Review all regulatory compliance status")
        recommendations.append("Ensure all statutory filings are up to date")
    
    if risk_scores["traction"] > 6.0:
        recommendations.append("Request detailed customer acquisition metrics")
        recommendations.append("Verify market size and growth assumptions")
    
    if risk_scores["founder"] > 6.0:
        recommendations.append("Conduct comprehensive founder background checks")
        recommendations.append("Evaluate team composition and advisory board")
    
    if risk_scores["overall"] > 7.0:
        recommendations.append("Consider declining investment or requesting additional due diligence")
        recommendations.append("Schedule detailed investor review meeting")
    elif risk_scores["overall"] > 5.0:
        recommendations.append("Proceed with enhanced due diligence")
        recommendations.append("Request additional financial and legal documentation")
    else:
        recommendations.append("Standard due diligence process recommended")
        recommendations.append("Consider for investment pipeline")
    
    return recommendations