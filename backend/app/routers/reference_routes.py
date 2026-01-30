from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..db import get_session
from ..models import Reference, ReferenceCreate, ReferenceUpdate, User
from ..deps import get_current_user

router = APIRouter(prefix="/references", tags=["references"])

def missing_fields(r: Reference):
    required = ["title", "authors", "year"]
    if r.ref_type == "journal":
        required += ["journal", "volume", "pages"]
    if r.ref_type == "book":
        required += ["publisher"]
    if r.ref_type == "web":
        required += ["url", "accessed_at"]
    miss = []
    for k in required:
        v = getattr(r, k, None)
        if v is None or (isinstance(v, str) and not v.strip()):
            miss.append(k)
    return miss

def format_gbt7714(r: Reference) -> str:
    # MVP：非常简化版（够演示），后续可迭代更严格规则
    authors = r.authors.replace("；", ";").strip()
    if r.ref_type == "journal":
        # 作者. 题名[J]. 刊名, 年, 卷(期): 页码. DOI
        vol_issue = f"{r.volume}({r.issue})" if r.issue else f"{r.volume}"
        doi_part = f" DOI:{r.doi}" if r.doi else ""
        return f"{authors}. {r.title}[J]. {r.journal}, {r.year}, {vol_issue}: {r.pages}.{doi_part}"
    if r.ref_type == "book":
        # 作者. 书名[M]. 出版地: 出版社, 年.
        return f"{authors}. {r.title}[M]. {r.publisher}, {r.year}."
    if r.ref_type == "web":
        # 作者. 题名[EB/OL]. URL (访问日期).
        return f"{authors}. {r.title}[EB/OL]. {r.url} ({r.accessed_at})."
    return f"{authors}. {r.title}. {r.year}."

@router.get("")
def list_refs(
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    refs = session.exec(select(Reference).where(Reference.user_id == user.id).order_by(Reference.id.desc())).all()
    return [
        {
            **r.model_dump(),
            "missing": missing_fields(r),
            "gbt7714": format_gbt7714(r),
        }
        for r in refs
    ]

@router.post("")
def create_ref(
    data: ReferenceCreate,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    ref = Reference(**data.model_dump(), user_id=user.id)
    session.add(ref)
    session.commit()
    session.refresh(ref)
    return {"id": ref.id}

@router.patch("/{ref_id}")
def update_ref(
    ref_id: int,
    data: ReferenceUpdate,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    ref = session.get(Reference, ref_id)
    if not ref or ref.user_id != user.id:
        raise HTTPException(status_code=404, detail="Not found")
    for k, v in data.model_dump().items():
        setattr(ref, k, v)
    session.add(ref)
    session.commit()
    return {"ok": True}

@router.delete("/{ref_id}")
def delete_ref(
    ref_id: int,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    ref = session.get(Reference, ref_id)
    if not ref or ref.user_id != user.id:
        raise HTTPException(status_code=404, detail="Not found")
    session.delete(ref)
    session.commit()
    return {"ok": True}

@router.get("/{ref_id}/format")
def get_format(
    ref_id: int,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    ref = session.get(Reference, ref_id)
    if not ref or ref.user_id != user.id:
        raise HTTPException(status_code=404, detail="Not found")
    return {"gbt7714": format_gbt7714(ref), "missing": missing_fields(ref)}