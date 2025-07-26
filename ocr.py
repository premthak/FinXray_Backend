import fitz  # PyMuPDF
import pdfplumber
import re
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealPDFProcessor:
    """Real PDF document processor - replaces the fake OCR system"""
    
    def __init__(self):
        self.supported_formats = ['.pdf']
        
    def extract_company_name(self, filename: str) -> str:
        """Extract company name from filename as fallback"""
        name = filename.split('.')[0]
        name = re.sub(r'[_-]', ' ', name)
        return name.title()
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract all text from PDF using PyMuPDF"""
        try:
            doc = fitz.open(file_path)
            full_text = ""
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                full_text += text + "\n"
            
            doc.close()
            return full_text
            
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {str(e)}")
            return ""
    
    def extract_financial_data(self, text: str) -> Dict[str, Any]:
        """Extract financial data from document text"""
        financial_data = {
            'revenue': None,
            'funding_raised': None,
            'employees': None,
            'founded_year': None,
            'burn_rate': None,
            'cash_balance': None,
            'growth_rate': None
        }
        
        # Revenue patterns
        revenue_patterns = [
            r'revenue[:\s]+[\$₹]?([\d,]+(?:\.\d+)?)\s*([MmBbKk]?)',
            r'sales[:\s]+[\$₹]?([\d,]+(?:\.\d+)?)\s*([MmBbKk]?)',
            r'turnover[:\s]+[\$₹]?([\d,]+(?:\.\d+)?)\s*([MmBbKk]?)'
        ]
        
        for pattern in revenue_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount = float(match.group(1).replace(',', ''))
                multiplier = match.group(2).upper() if match.group(2) else ''
                
                if multiplier == 'K':
                    amount *= 1000
                elif multiplier == 'M':
                    amount *= 1000000
                elif multiplier == 'B':
                    amount *= 1000000000
                    
                financial_data['revenue'] = amount
                break
        
        # Funding patterns
        funding_patterns = [
            r'raised[:\s]+[\$₹]?([\d,]+(?:\.\d+)?)\s*([MmBbKk]?)',
            r'funding[:\s]+[\$₹]?([\d,]+(?:\.\d+)?)\s*([MmBbKk]?)',
            r'investment[:\s]+[\$₹]?([\d,]+(?:\.\d+)?)\s*([MmBbKk]?)'
        ]
        
        for pattern in funding_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount = float(match.group(1).replace(',', ''))
                multiplier = match.group(2).upper() if match.group(2) else ''
                
                if multiplier == 'K':
                    amount *= 1000
                elif multiplier == 'M':
                    amount *= 1000000
                elif multiplier == 'B':
                    amount *= 1000000000
                    
                financial_data['funding_raised'] = amount
                break
        
        # Employee count patterns
        employee_patterns = [
            r'employees?[:\s]+(\d+)',
            r'team[:\s]+(\d+)',
            r'staff[:\s]+(\d+)'
        ]
        
        for pattern in employee_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                financial_data['employees'] = int(match.group(1))
                break
        
        # Founded year patterns
        year_patterns = [
            r'founded[:\s]+(\d{4})',
            r'established[:\s]+(\d{4})',
            r'started[:\s]+(\d{4})'
        ]
        
        for pattern in year_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                year = int(match.group(1))
                if 1900 <= year <= datetime.now().year:
                    financial_data['founded_year'] = year
                break
        
        return financial_data
    
    def extract_key_metrics(self, text: str) -> Dict[str, Any]:
        """Extract key business metrics from document"""
        metrics = {
            'business_model': None,
            'market_size': None,
            'competitors': [],
            'technology_stack': [],
            'legal_structure': None
        }
        
        # Business model detection
        if re.search(r'(subscription|saas|recurring)', text, re.IGNORECASE):
            metrics['business_model'] = 'Subscription/SaaS'
        elif re.search(r'(marketplace|platform|commission)', text, re.IGNORECASE):
            metrics['business_model'] = 'Marketplace/Platform'
        elif re.search(r'(e-commerce|online store)', text, re.IGNORECASE):
            metrics['business_model'] = 'E-commerce'
        
        # Market size patterns
        market_patterns = [
            r'market size[:\s]+[\$₹]?([\d,]+(?:\.\d+)?)\s*([MmBbKk]?)',
            r'addressable market[:\s]+[\$₹]?([\d,]+(?:\.\d+)?)\s*([MmBbKk]?)'
        ]
        
        for pattern in market_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount = float(match.group(1).replace(',', ''))
                multiplier = match.group(2).upper() if match.group(2) else ''
                
                if multiplier == 'M':
                    amount *= 1000000
                elif multiplier == 'B':
                    amount *= 1000000000
                    
                metrics['market_size'] = amount
                break
        
        # Extract competitor mentions
        competitor_patterns = [
            r'competitors?[:\s]+([A-Z][a-zA-Z\s,]+)',
            r'competing with[:\s]+([A-Z][a-zA-Z\s,]+)'
        ]
        
        for pattern in competitor_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                competitors_text = match.group(1)
                competitors = [comp.strip() for comp in re.split(r'[,;]', competitors_text)]
                metrics['competitors'] = [comp for comp in competitors if len(comp) > 2][:5]
                break
        
        return metrics

def process_uploaded_pdf(file_path: str, filename: str) -> Dict[str, Any]:
    """
    MAIN FUNCTION - Replace your existing process_uploaded_pdf function with this
    """
    try:
        processor = RealPDFProcessor()
        
        # Extract company name from filename
        company_name = processor.extract_company_name(filename)
        
        # Extract text from PDF
        logger.info(f"Processing PDF: {filename}")
        full_text = processor.extract_text_from_pdf(file_path)
        
        if not full_text:
            logger.warning(f"No text extracted from {filename}")
            return {
                'company_name': company_name,
                'error': 'Could not extract text from PDF',
                'extraction_successful': False
            }
        
        # Extract financial data
        financial_data = processor.extract_financial_data(full_text)
        
        # Extract key metrics
        key_metrics = processor.extract_key_metrics(full_text)
        
        # Combine all extracted data
        result = {
            'company_name': company_name,
            'extraction_successful': True,
            'document_length': len(full_text),
            'financial_data': financial_data,
            'key_metrics': key_metrics,
            'raw_text_sample': full_text[:500] + "..." if len(full_text) > 500 else full_text,
            'processed_timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Successfully processed PDF for {company_name}")
        return result
        
    except Exception as e:
        logger.error(f"Error processing PDF {filename}: {str(e)}")
        return {
            'company_name': processor.extract_company_name(filename) if 'processor' in locals() else 'Unknown',
            'error': str(e),
            'extraction_successful': False
        }


