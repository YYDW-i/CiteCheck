from fastapi import APIRouter, HTTPException
import httpx

router = APIRouter(prefix="/doi", tags=["doi"])

def normalize(doi: str) -> str:
    doi = doi.strip()
    doi = doi.replace("https://doi.org/", "").replace("http://doi.org/", "")
    doi = doi.replace("doi:", "").strip()
    return doi

async def fetch_json(url: str, headers=None):
    async with httpx.AsyncClient(timeout=10, headers={"User-Agent":"CiteCheck/1.0"}) as client:
        r = await client.get(url, headers=headers)
        if r.status_code != 200:
            return None
        return r.json()

@router.get("/resolve")
async def resolve(doi: str):
    d = normalize(doi)
    if not d.startswith("10."):
        raise HTTPException(400, "Invalid DOI")

    # 1) Crossref
    data = await fetch_json(f"https://api.crossref.org/works/{d}")
    if data:
        msg = data.get("message", {})
        title = (msg.get("title") or [""])[0]
        authors = ";".join([
            " ".join([a.get("family",""), a.get("given","")]).strip()
            for a in (msg.get("author") or [])
        ]).strip(";")
        year = None
        for k in ["published-print","published-online","created","issued"]:
            parts = (msg.get(k) or {}).get("date-parts") or []
            if parts and parts[0]:
                year = parts[0][0]; break
        return {"ok": True, "source":"crossref", "doi": d, "title": title, "authors": authors, "year": year}

    # 2) OpenAlex
    data = await fetch_json(f"https://api.openalex.org/works/https://doi.org/{d}")
    if data:
        title = (data.get("title") or "").strip()
        year = data.get("publication_year")
        authors = ";".join([
            (a.get("author") or {}).get("display_name","")
            for a in (data.get("authorships") or [])
        ]).strip(";")
        return {"ok": True, "source":"openalex", "doi": d, "title": title, "authors": authors, "year": year}

    # 3) Semantic Scholar
    data = await fetch_json(
        f"https://api.semanticscholar.org/graph/v1/paper/DOI:{d}?fields=title,year,authors"
    )
    if data:
        title = (data.get("title") or "").strip()
        year = data.get("year")
        authors = ";".join([a.get("name","") for a in (data.get("authors") or [])]).strip(";")
        return {"ok": True, "source":"semanticscholar", "doi": d, "title": title, "authors": authors, "year": year}

    # 4) DOI content negotiation (CSL-JSON)
    async with httpx.AsyncClient(timeout=10, headers={"User-Agent":"CiteCheck/1.0"}) as client:
        r = await client.get(f"https://doi.org/{d}", headers={"Accept":"application/vnd.citationstyles.csl+json"})
        if r.status_code == 200:
            j = r.json()
            title = (j.get("title") or "").strip()
            issued = (j.get("issued") or {}).get("date-parts") or []
            year = issued[0][0] if issued and issued[0] else None
            authors = ";".join([
                " ".join([a.get("family",""), a.get("given","")]).strip()
                for a in (j.get("author") or [])
            ]).strip(";")
            return {"ok": True, "source":"doi_csl", "doi": d, "title": title, "authors": authors, "year": year}

    # CNKI 常见：开放库里确实没有
    return {
        "ok": False,
        "doi": d,
        "detail": "开放数据库未收录（Crossref/OpenAlex/S2/doi.org 均无元数据）。CNKI 文献建议用 RIS/BibTeX 导出后导入。",
    }
