"""
StartupDataFetcher
Fetches real-time startup data from MCA filings, company databases,
and public APIs so your dashboard can show complete investor-grade details.
"""

import os
import asyncio
import aiohttp
from typing import Dict, Any, List
from dotenv import load_dotenv

load_dotenv()  # Loads API keys from backend/.env

# ────────────────────────────────────────────────────────────────
# Helper functions
# ────────────────────────────────────────────────────────────────
async def _fetch_json(session: aiohttp.ClientSession, url: str, headers=None) -> Dict[str, Any]:
    async with session.get(url, headers=headers, timeout=30) as resp:
        resp.raise_for_status()
        return await resp.json()


# ────────────────────────────────────────────────────────────────
# Main class
# ────────────────────────────────────────────────────────────────
class StartupDataFetcher:
    """Grabs data from MCA, Perplexity AI, Crunchbase-like sources, and Alpha Vantage."""

    def __init__(self) -> None:
        self.mca_key = os.getenv("MCA_API_KEY")
        self.perplexity_key = os.getenv("PERPLEXITY_API_KEY")
        self.alpha_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        self.headers = {"User-Agent": "FinXrayBot/1.0"}

    # ─────────────────────────────────────────────
    # PUBLIC METHOD the backend will call
    # ─────────────────────────────────────────────
    async def fetch_startup_profile(self, company_name: str, domain: str) -> Dict[str, Any]:
        """
        Returns a single JSON object with every data-point investors expect:
        MCA status, funding, founders, market size, KPI snapshots, risk score, etc.
        """
        async with aiohttp.ClientSession() as session:
            profile_tasks: List[asyncio.Task] = [
                asyncio.create_task(self._get_mca_data(session, company_name)),
                asyncio.create_task(self._get_perplexity_analysis(session, company_name, domain)),
                asyncio.create_task(self._get_market_data(session, domain)),
            ]

            mca_data, perplexity_data, market_data = await asyncio.gather(*profile_tasks)

        # ── Minimal merge; extend as needed ──
        combined = {
            "company_name": company_name,
            "domain": domain,
            "mca": mca_data,
            "analysis": perplexity_data,
            "market": market_data,
        }
        combined["risk_score"] = self._calculate_risk_score(combined)
        combined["recommendation"] = self._investment_recommendation(combined["risk_score"])
        return combined

    # ─────────────────────────────────────────────
    # PRIVATE HELPERS
    # ─────────────────────────────────────────────
    async def _get_mca_data(self, session: aiohttp.ClientSession, company_name: str) -> Dict[str, Any]:
        """Pulls latest MCA filing data (India)"""
        if not self.mca_key:
            return {"error": "Missing MCA_API_KEY"}
        url = f"https://api.mca.gov.in/v1/companies/{company_name}?api_key={self.mca_key}"
        try:
            return await _fetch_json(session, url, headers=self.headers)
        except Exception as exc:
            return {"error": f"MCA fetch failed: {exc}"}

    async def _get_perplexity_analysis(
        self, session: aiohttp.ClientSession, company_name: str, domain: str
    ) -> Dict[str, Any]:
        """Gets deep-dive analysis from Perplexity AI using your custom prompt."""
        if not self.perplexity_key:
            return {"error": "Missing PERPLEXITY_API_KEY"}

        prompt = (
            f"Give a comprehensive investor analysis of {company_name} operating in {domain}. "
            "Cover founders, market size, traction, competitors, financial health, risks, "
            "and provide an INVEST/CONSIDER/AVOID recommendation."
        )
        url = "https://api.perplexity.ai/chat/completions"
        payload = {
            "model": "pplx-70b-chat",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 800,
        }
        headers = {
            "Authorization": f"Bearer {self.perplexity_key}",
            "Content-Type": "application/json",
        }
        async with session.post(url, json=payload, headers=headers, timeout=60) as resp:
            resp.raise_for_status()
            data = await resp.json()
        return {"analysis_text": data["choices"][0]["message"]["content"]}

    async def _get_market_data(self, session: aiohttp.ClientSession, domain: str) -> Dict[str, Any]:
        """Example market-sizing fetch (dummy Alpha Vantage call)."""
        if not self.alpha_key:
            return {"error": "Missing ALPHA_VANTAGE_API_KEY"}
        # Replace with real endpoint for market data
        url = f"https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={domain}&apikey={self.alpha_key}"
        try:
            return await _fetch_json(session, url, headers=self.headers)
        except Exception as exc:
            return {"error": f"Market fetch failed: {exc}"}

    def _calculate_risk_score(self, data: Dict[str, Any]) -> int:
        """Very simple placeholder risk score algorithm."""
        mca_good = data["mca"].get("status") == "Active"
        return 40 if mca_good else 70  # lower is better

    def _investment_recommendation(self, score: int) -> str:
        """Map score to INVEST / CONSIDER / AVOID."""
        if score < 50:
            return "INVEST"
        if score < 70:
            return "CONSIDER"
        return "AVOID"
