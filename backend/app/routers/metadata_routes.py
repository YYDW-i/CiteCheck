from fastapi import APIRouter, HTTPException
import httpx

router = APIRouter(prefix="/metadata", tags=["metadata"])

@router.get("/doi/{doi:path}")
async def fetch_by_doi(doi: str):
    # Crossref Works API
    url = f"https://api.crossref.org/works/{doi}"
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url, headers={"User-Agent": "CiteCheck/0.1 (mailto:example@example.com)"})
    if r.status_code != 200:
        raise HTTPException(status_code=404, detail="DOI not found on Crossref")
    msg = r.json().get("message", {})

    # MVP：提取常用字段
    title = (msg.get("title") or [""])[0]
    authors_list = []
    for a in msg.get("author") or []:
        given = a.get("given", "")
        family = a.get("family", "")
        name = (family + given).strip() or (given + " " + family).strip()
        if name:
            authors_list.append(name)
    authors = "; ".join(authors_list)

    year = None
    issued = msg.get("issued", {}).get("date-parts", [])
    if issued and issued[0] and issued[0][0]:
        year = issued[0][0]

    journal = (msg.get("container-title") or [""])[0]
    volume = msg.get("volume")
    issue = msg.get("issue")
    pages = msg.get("page")

    url2 = msg.get("URL")
    return {
        "title": title,
        "authors": authors,
        "year": year,
        "journal": journal,
        "volume": volume,
        "issue": issue,
        "pages": pages,
        "doi": doi,
        "url": url2,
    }