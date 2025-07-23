# company_enrichment.py
"""
FinXray – external data fetcher
Uses Clearbit, OpenCorporates and Crunchbase in parallel.
"""
import os, httpx, asyncio
from typing import Dict, Any

CLEARBIT_KEY = os.getenv("CLEARBIT_KEY")
OPENC_API   = os.getenv("OPENC_API")          # OpenCorporates API token
CRUNCH_KEY  = os.getenv("CRUNCH_KEY")         # Crunchbase user key

async def clearbit_lookup(name: str) -> Dict[str, Any]:
    """Return firmographics from Clearbit Name-to-Domain + Company APIs."""
    try:
        async with httpx.AsyncClient(timeout=12) as client:
            r = await client.get(
                "https://company.clearbit.com/v2/companies/find",
                params={"name": name},
                auth=(CLEARBIT_KEY, "")
            )
            return r.json() if r.status_code == 200 else {}
    except Exception:
        return {}

            return r.json() if r.status_code == 200 else {}
    except:
        return {}

async def opencorp_lookup(name: str) -> Dict[str, Any]:
    """Return first matching legal entity from OpenCorporates."""
    try:
        async with httpx.AsyncClient(timeout=12) as client:
            r = await client.get(
                f"https://api.opencorporates.com/v0.4/companies/search",
                params={"q": name, "api_token": OPENC_API, "per_page": 1}
            )
            data = r.json()
            return data["results"]["companies"][0]["company"] if (
                r.status_code == 200 and data.get("results", {}).get("companies")
            ) else {}
    except:
        return {}

async def crunchbase_lookup(name: str) -> Dict[str, Any]:
    """Return funding + category info from Crunchbase."""
    try:
        async with httpx.AsyncClient(timeout=12) as client:
            r = await client.get(
                "https://api.crunchbase.com/api/v4/autocompletes",
                params={"query": name, "collection_ids": "organizations", "limit": 1},
                headers={"X-cb-user-key": CRUNCH_KEY}
            )
            items = r.json().get("entities", [])
            return items[0] if items else {}
    except:
        return {}

async def enrich_company(name: str) -> Dict[str, Any]:
    """Orchestrates all three calls concurrently."""
    tasks = [clearbit_lookup(name), opencorp_lookup(name), crunchbase_lookup(name)]
    clear, oc, cb = await asyncio.gather(*tasks)
    return {
        "company_name": name,
        "clearbit": clear,
        "opencorporates": oc,
        "crunchbase": cb,
        "found_data": bool(clear or oc or cb)
    }
