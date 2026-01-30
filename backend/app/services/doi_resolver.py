from __future__ import annotations
from typing import Any, Dict, Optional, Tuple, List
import httpx

CSL_ACCEPT = "application/vnd.citationstyles.csl+json"

def normalize_doi(doi: str) -> str:
    d = doi.strip()
    d = d.replace("https://doi.org/", "").replace("http://doi.org/", "")
    d = d.replace("doi:", "").strip()
    return d

def _authors_from_crossref(msg: Dict[str, Any]) -> str:
    authors = msg.get("author") or []
    parts: List[str] = []
    for a in authors:
        family = (a.get("family") or "").strip()
        given = (a.get("given") or "").strip()
        name = " ".join([x for x in [family, given] if x]).strip()
        if name:
            parts.append(name)
    return ";".join(parts)

def _year_from_crossref(msg: Dict[str, Any]) -> Optional[int]:
    for k in ["published-print", "published-online", "created", "issued"]:
        parts = (msg.get(k) or {}).get("date-parts") or []
        if parts and parts[0]:
            y = parts[0][0]
            if isinstance(y, int):
                return y
    return None

async def _get_json(client: httpx.AsyncClient, url: str, headers: Optional[Dict[str, str]] = None) -> Tuple[int, Any]:
    r = await client.get(url, headers=headers)
    ct = r.headers.get("content-type", "")
    if "application/json" in ct:
        return r.status_code, r.json()
    return r.status_code, r.text

async def try_crossref(client: httpx.AsyncClient, doi: str) -> Optional[Dict[str, Any]]:
    # Crossref: /works/{doi} :contentReference[oaicite:1]{index=1}
    url = f"https://api.crossref.org/works/{doi}"
    code, data = await _get_json(client, url)
    if code != 200 or not isinstance(data, dict):
        return None
    msg = data.get("message") or {}
    title = (msg.get("title") or [""])[0]
    authors = _authors_from_crossref(msg)
    year = _year_from_crossref(msg)
    return {"doi": doi, "title": title, "authors": authors, "year": year, "source": "crossref"}

async def try_datacite(client: httpx.AsyncClient, doi: str) -> Optional[Dict[str, Any]]:
    # DataCite REST API commonly used: api.datacite.org/dois/{doi}
    url = f"https://api.datacite.org/dois/{doi}"
    code, data = await _get_json(client, url)
    if code != 200 or not isinstance(data, dict):
        return None
    attr = ((data.get("data") or {}).get("attributes")) or {}
    title = ""
    titles = attr.get("titles") or []
    if titles:
        title = (titles[0].get("title") or "").strip()
    creators = attr.get("creators") or []
    authors = ";".join([(c.get("name") or "").strip() for c in creators if (c.get("name") or "").strip()])
    year = attr.get("publicationYear")
    return {"doi": doi, "title": title, "authors": authors, "year": year, "source": "datacite"}

async def try_openalex(client: httpx.AsyncClient, doi: str) -> Optional[Dict[str, Any]]:
    # OpenAlex: works can be fetched by external IDs, including DOI URL form :contentReference[oaicite:2]{index=2}
    url = f"https://api.openalex.org/works/https://doi.org/{doi}"
    code, data = await _get_json(client, url)
    if code != 200 or not isinstance(data, dict):
        return None
    title = (data.get("title") or "").strip()
    year = data.get("publication_year")
    authorships = data.get("authorships") or []
    names = []
    for au in authorships:
        a = (au.get("author") or {}).get("display_name")
        if a:
            names.append(a)
    authors = ";".join(names)
    return {"doi": doi, "title": title, "authors": authors, "year": year, "source": "openalex"}

async def try_semantic_scholar(client: httpx.AsyncClient, doi: str) -> Optional[Dict[str, Any]]:
    # Semantic Scholar Academic Graph API: paper id can be DOI:<doi> :contentReference[oaicite:3]{index=3}
    fields = "title,year,authors"
    url = f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}?fields={fields}"
    code, data = await _get_json(client, url)
    if code != 200 or not isinstance(data, dict):
        return None
    title = (data.get("title") or "").strip()
    year = data.get("year")
    authors = ";".join([a.get("name") for a in (data.get("authors") or []) if a.get("name")])
    return {"doi": doi, "title": title, "authors": authors, "year": year, "source": "semanticscholar"}

async def try_doi_csl(client: httpx.AsyncClient, doi: str) -> Optional[Dict[str, Any]]:
    # DOI content negotiation: Accept: application/vnd.citationstyles.csl+json :contentReference[oaicite:4]{index=4}
    url = f"https://doi.org/{doi}"
    headers = {"Accept": CSL_ACCEPT}
    code, data = await _get_json(client, url, headers=headers)
    if code != 200 or not isinstance(data, dict):
        return None

    title = (data.get("title") or "").strip()
    year = None
    issued = (data.get("issued") or {}).get("date-parts") or []
    if issued and issued[0]:
        year = issued[0][0]
    author_list = data.get("author") or []
    names = []
    for a in author_list:
        family = (a.get("family") or "").strip()
        given = (a.get("given") or "").strip()
        nm = " ".join([x for x in [family, given] if x]).strip()
        if nm:
            names.append(nm)
    authors = ";".join(names)
    return {"doi": doi, "title": title, "authors": authors, "year": year, "source": "doi_csl"}

async def resolve_doi_multi(doi_raw: str) -> Dict[str, Any]:
    doi = normalize_doi(doi_raw)
    if not doi.startswith("10."):
        return {"ok": False, "detail": "Invalid DOI format", "doi": doi}

    # 依次尝试：Crossref → DataCite → OpenAlex → S2 → doi.org(csl)
    # 顺序解释：优先权威登记元数据，其次覆盖面，再兜底 content negotiation
    async with httpx.AsyncClient(timeout=10, headers={"User-Agent": "CiteCheck/1.0"}) as client:
        for fn in [try_crossref, try_datacite, try_openalex, try_semantic_scholar, try_doi_csl]:
            try:
                hit = await fn(client, doi)
                if hit and (hit.get("title") or hit.get("authors") or hit.get("year")):
                    hit["ok"] = True
                    return hit
            except Exception:
                # 单个来源挂了不影响后续来源
                continue

    # 都没查到：对 CNKI/国内期刊很常见
    return {
        "ok": False,
        "doi": doi,
        "detail": "No metadata found in open sources (Crossref/DataCite/OpenAlex/S2/doi.org). For CNKI journals, please export RIS/BibTeX and import.",
    }
