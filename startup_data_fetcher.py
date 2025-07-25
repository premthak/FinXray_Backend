"""
startup_data_fetcher.py
-----------------------------------------------------------------
Central helper class that gathers public-domain information about
a startup and formats it for the FinXray risk-analysis pipeline.

Replace the TODO blocks with real API calls (Crunchbase, Clearbit,
OpenCorporates, etc.) when you are ready.  All external requests
are isolated in their own private _fetch_* methods so you can
enable / disable individual sources without touching the main
public interface.
"""

import asyncio
from typing import Dict, Any, List, Optional

import aiohttp


class StartupDataFetcher:
    """
    Asynchronous façade that aggregates data from multiple
    third-party APIs and returns a single, clean dict a.k.a.
    “startup profile” ready for scoring.
    """

    # ------------------------------------------------------------------
    # 1. Public interface
    # ------------------------------------------------------------------
    async def fetch_startup_profile(self, company_name: str, domain: str) -> Dict[str, Any]:
        """
        Main entry point called by FastAPI.

        Parameters
        ----------
        company_name : str
            Plain-text company name from the frontend form.
        domain : str
            Industry / domain keyword supplied by the user.

        Returns
        -------
        Dict[str, Any]
            Merged and lightly cleaned data ready for risk_model.py
        """
        if not self._validate_inputs(company_name, domain):
            return {
                "error": "Both company_name and domain must be non-empty strings."
            }

        # Kick off all API calls in parallel
        crunchbase_task   = asyncio.create_task(self._fetch_crunchbase(company_name))
        clearbit_task     = asyncio.create_task(self._fetch_clearbit(company_name))
        opencorp_task     = asyncio.create_task(self._fetch_opencorporates(company_name))

        # Wait for them to complete
        crunchbase_data   = await crunchbase_task
        clearbit_data     = await clearbit_task
        opencorp_data     = await opencorp_task

        # Merge responses
        profile: Dict[str, Any] = {
            "company_name": company_name,
            "domain": domain,
            "sources": {},
            "found_data": False
        }

        # Helper to merge if data returned
        def _merge(source: str, payload: Optional[Dict[str, Any]]):
            if payload:
                profile["sources"][source] = payload
                profile["found_data"] = True

        _merge("crunchbase", crunchbase_data)
        _merge("clearbit", clearbit_data)
        _merge("opencorporates", opencorp_data)

        return profile

    # ------------------------------------------------------------------
    # 2. Private helpers (one per external provider)
    #    Replace the `TODO` sections with real implementation.
    # ------------------------------------------------------------------
    async def _fetch_crunchbase(self, company: str) -> Optional[Dict[str, Any]]:
        """Query Crunchbase API (placeholder)."""
        # TODO: add your Crunchbase key and real URL
        # Example curl:
        #   GET https://api.crunchbase.com/v4/entities/organizations?name=<company>&user_key=<API_KEY>
        return None  # Returning None means “no data or provider disabled”

    async def _fetch_clearbit(self, company: str) -> Optional[Dict[str, Any]]:
        """Query Clearbit Enrichment API (placeholder)."""
        # TODO: add your Clearbit key and real URL
        return None

    async def _fetch_opencorporates(self, company: str) -> Optional[Dict[str, Any]]:
        """Query OpenCorporates API (placeholder)."""
        # Free tier does not need auth
        url = f"https://api.opencorporates.com/v0.4/companies/search?q={company}"
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15)) as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        # Trim response to essentials
                        companies: List[Dict[str, Any]] = data.get("results", {}).get("companies", [])
                        if companies:
                            first = companies[0]["company"]
                            return {
                                "jurisdiction": first.get("jurisdiction_code"),
                                "company_number": first.get("company_number"),
                                "incorporation_date": first.get("incorporation_date"),
                                "current_status": first.get("current_status"),
                                "registered_address": first.get("registered_address")
                            }
        except Exception as exc:
            # Log locally; upstream code can decide whether to surface error
            print(f"[OpenCorporates] error: {exc}")
        return None

    # ------------------------------------------------------------------
    # 3. Utility
    # ------------------------------------------------------------------
    @staticmethod
    def _validate_inputs(name: str, domain: str) -> bool:
        return bool(name and name.strip() and domain and domain.strip())

