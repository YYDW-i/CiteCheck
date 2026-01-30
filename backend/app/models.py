from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field
from pydantic import BaseModel

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Reference(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)

    # 基础字段
    ref_type: str = Field(default="journal")  # journal/book/web
    title: str
    authors: str  # MVP 先用字符串："张三; 李四"
    year: Optional[int] = None

    # 期刊
    journal: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None

    # 图书/出版
    publisher: Optional[str] = None
    isbn: Optional[str] = None

    # 通用
    doi: Optional[str] = None
    url: Optional[str] = None
    accessed_at: Optional[str] = None  # "2026-01-29"

    created_at: datetime = Field(default_factory=datetime.utcnow)

class ReferenceCreate(BaseModel):
    ref_type: str = "journal"
    title: str
    authors: str
    year: Optional[int] = None
    journal: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None
    publisher: Optional[str] = None
    isbn: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    accessed_at: Optional[str] = None

class ReferenceUpdate(ReferenceCreate):
    pass