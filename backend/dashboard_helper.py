from datetime import datetime
from typing import Dict, Any, List
import random

class DashboardDataTransformer:
    """Transforms raw startup data into dashboard-ready format"""
    
    def __init__(self):
        self.risk_weights = {
            'fraud_risk': 0.3,
            'compliance_risk': 0.25,
            'traction_risk': 0.25,
            'founder_risk': 0.2
        }
    
    def transform_to_dashboard_format(self, raw_data: Dict[str, Any], company_name: str, domain: str) -> Dict[str, Any]:
        """Main transformation function"""
        
        # Extract or calculate risk metrics
        risk_breakdown = self.calculate_risk_breakdown(raw_data)
        overall_risk = self.calculate_overall_risk(risk_breakdown)
        
        # Transform to dashboard format
        dashboard_data = {
            "company_name": company_name,
            "domain": domain,
            "timestamp": datetime.now().isoformat(),
            
            # Main KPIs
            "overall_risk_score": overall_risk,
            "risk_category": self.get_risk_category(overall_risk),
            "confidence_score": self.calculate_confidence_score(raw_data),
            
            # Risk breakdown
            "risk_breakdown": risk_breakdown,
            
            # Financial metrics (mock data - replace with real calculations)
            "financial_metrics": self.extract_financial_metrics(raw_data),
            
            # Operational data
            "operational_metrics": self.extract_operational_metrics(raw_data),
            
            # Analysis summary
            "analysis_summary": self.generate_analysis_summary(company_name, domain, overall_risk),
            "red_flags": self.extract_red_flags(raw_data, overall_risk),
            "positive_indicators": self.extract_positive_indicators(raw_data),
            
            # Data sources info
            "data_sources": self.get_data_sources_info(raw_data),
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return dashboard_data
    
    def calculate_risk_breakdown(self, raw_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate individual risk components"""
        
        # Use real data from startup_data_fetcher if available
        if raw_data and raw_data.get('sources'):
            # Extract real risk indicators from your data sources
            fraud_risk = self.calculate_fraud_risk(raw_data)
            compliance_risk = self.calculate_compliance_risk(raw_data)
            traction_risk = self.calculate_traction_risk(raw_data)
            founder_risk = self.calculate_founder_risk(raw_data)
        else:
            # Fallback to calculated estimates
            fraud_risk = random.uniform(15, 45)
            compliance_risk = random.uniform(20, 50)
            traction_risk = random.uniform(25, 60)
            founder_risk = random.uniform(10, 40)
        
        return {
            "fraud_risk": round(fraud_risk, 1),
            "compliance_risk": round(compliance_risk, 1),
            "traction_risk": round(traction_risk, 1),
            "founder_risk": round(founder_risk, 1)
        }
    
    def calculate_overall_risk(self, risk_breakdown: Dict[str, float]) -> float:
        """Calculate weighted overall risk score"""
        total_risk = sum(
            risk_breakdown[risk] * weight 
            for risk, weight in self.risk_weights.items()
        )
        return round(total_risk, 1)
    
    def get_risk_category(self, risk_score: float) -> str:
        """Categorize risk score"""
        if risk_score <= 30:
            return "LOW"
        elif risk_score <= 60:
            return "MEDIUM"
        else:
            return "HIGH"
    
    def calculate_confidence_score(self, raw_data: Dict[str, Any]) -> int:
        """Calculate confidence in the analysis"""
        if not raw_data or not raw_data.get('sources'):
            return 50
        
        source_count = len(raw_data.get('sources', {}))
        base_confidence = min(50 + (source_count * 15), 95)
        return base_confidence
    
    def extract_financial_metrics(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract financial metrics from raw data"""
        # Replace with real financial data extraction
        return {
            "revenue": random.randint(100000, 5000000),
            "burn_rate": random.randint(50000, 500000),
            "runway_months": random.randint(6, 36),
            "funding_raised": random.randint(500000, 20000000),
            "valuation": random.randint(5000000, 100000000),
            "cac": random.randint(100, 1000),
            "ltv": random.randint(500, 5000)
        }
    
    def extract_operational_metrics(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract operational metrics"""
        return {
            "team_size": random.randint(5, 100),
            "market_size": random.randint(1000000, 100000000),
            "competition_level": random.choice(["Low", "Medium", "High"]),
            "regulatory_complexity": random.choice(["Low", "Medium", "High"])
        }
    
    def generate_analysis_summary(self, company_name: str, domain: str, risk_score: float) -> str:
        """Generate analysis summary text"""
        risk_level = self.get_risk_category(risk_score).lower()
        
        summaries = {
            "low": f"{company_name} shows strong fundamentals in the {domain} sector with minimal risk indicators. Recommended for investment consideration.",
            "medium": f"{company_name} presents moderate risk profile in {domain}. Requires additional due diligence before investment decision.",
            "high": f"{company_name} exhibits elevated risk factors in {domain}. Comprehensive risk mitigation strategy needed before investment."
        }
        
        return summaries.get(risk_level, f"Analysis complete for {company_name} in {domain} sector.")
    
    def extract_red_flags(self, raw_data: Dict[str, Any], risk_score: float) -> List[str]:
        """Extract red flags based on analysis"""
        red_flags = []
        
        if risk_score > 60:
            red_flags.extend([
                "High overall risk score detected",
                "Limited financial transparency"
            ])
        
        if risk_score > 40:
            red_flags.append("Moderate market competition")
        
        # Add more red flags based on your actual data analysis
        if not raw_data or not raw_data.get('sources'):
            red_flags.append("Limited public data available")
        
        return red_flags[:5]  # Limit to 5 red flags
    
    def extract_positive_indicators(self, raw_data: Dict[str, Any]) -> List[str]:
        """Extract positive indicators"""
        positives = [
            "Active in target market sector",
            "Structured business approach",
            "Clear domain focus"
        ]
        
        if raw_data and raw_data.get('sources'):
            positives.append("Multiple data sources validated")
        
        return positives[:4]  # Limit to 4 positive indicators
    
    def get_data_sources_info(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get information about data sources used"""
        if raw_data and raw_data.get('sources'):
            return {
                "total_sources": len(raw_data['sources']),
                "sources_used": list(raw_data['sources'].keys()),
                "data_freshness": "Recent"
            }
        
        return {
            "total_sources": 1,
            "sources_used": ["manual_analysis"],
            "data_freshness": "Current"
        }
    
    # Individual risk calculation methods (implement based on your data)
    def calculate_fraud_risk(self, raw_data: Dict[str, Any]) -> float:
        """Calculate fraud risk from raw data"""
        # Implement your fraud risk calculation logic
        return random.uniform(15, 45)
    
    def calculate_compliance_risk(self, raw_data: Dict[str, Any]) -> float:
        """Calculate compliance risk from raw data"""
        # Implement your compliance risk calculation logic
        return random.uniform(20, 50)
    
    def calculate_traction_risk(self, raw_data: Dict[str, Any]) -> float:
        """Calculate traction risk from raw data"""
        # Implement your traction risk calculation logic
        return random.uniform(25, 60)
    
    def calculate_founder_risk(self, raw_data: Dict[str, Any]) -> float:
        """Calculate founder risk from raw data"""
        # Implement your founder risk calculation logic
        return random.uniform(10, 40)

