import re

def analyze_document(file_content, industry):
    text = file_content.decode("utf-8", errors="ignore")

    extracted = {
        "revenue": extract_number(text, r"(revenue|income)[\s:₹$]*([\d,.]+)"),
        "expenses": extract_number(text, r"(expenses|cost)[\s:₹$]*([\d,.]+)"),
        "profit": extract_number(text, r"(profit|net income)[\s:₹$]*([\d,.]+)"),
        "valuation": extract_number(text, r"(valuation|worth)[\s:₹$]*([\d,.]+)")
    }

    # Red Flag Logic
    extracted["red_flags"] = []
    if extracted["expenses"] and extracted["revenue"] and extracted["expenses"] > extracted["revenue"]:
        extracted["red_flags"].append("Expenses higher than revenue.")
    if not extracted["valuation"]:
        extracted["red_flags"].append("No valuation data mentioned.")

    # Sample AI KPI scores
    extracted["ai_kpi_score"] = 82  # Later: model-based
    extracted["financial_kpi_score"] = 76

    return extracted

def extract_number(text, pattern):
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        num = match.group(2).replace(",", "")
        try:
            return float(num)
        except:
            return None
    return None
