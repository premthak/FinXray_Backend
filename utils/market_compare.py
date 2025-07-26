def compare_to_market(data, industry):
    # Static sample; later use live API
    industry_avg = {
        "general": {
            "profit_margin": 15,
            "valuation_range": (1_000_000, 10_000_000),
        }
    }

    comparison = {}
    if data["profit"] and data["revenue"]:
        actual_margin = (data["profit"] / data["revenue"]) * 100
        comparison["profit_margin_vs_industry"] = actual_margin - industry_avg[industry]["profit_margin"]

    if data["valuation"]:
        min_val, max_val = industry_avg[industry]["valuation_range"]
        if data["valuation"] < min_val:
            comparison["valuation_flag"] = "Low valuation for industry"
        elif data["valuation"] > max_val:
            comparison["valuation_flag"] = "Unusually high valuation"

    return comparison
