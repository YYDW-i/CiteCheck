from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db import init_db
from .routers.auth_routes import router as auth_router
from .routers.reference_routes import router as ref_router
from .routers.metadata_routes import router as meta_router
from sqlmodel import SQLModel
from .db import engine
from .routers.doi_routes import router as doi_router




app = FastAPI(title="CiteCheck API")
app.include_router(doi_router)
from fastapi import Request
from fastapi.responses import JSONResponse
import traceback


@app.exception_handler(Exception)
async def all_exception_handler(request: Request, exc: Exception):
    # 让前端能看到后端到底炸在哪（开发用，做完项目可删掉）
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal Server Error",
            "error": str(exc),
            "trace": traceback.format_exc(),
            "path": str(request.url),
        },
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()
    SQLModel.metadata.create_all(engine)

app.include_router(auth_router)
app.include_router(ref_router)
app.include_router(meta_router)

@app.get("/health")
def health():
    return {"ok": True}
from pathlib import Path
from fastapi.responses import FileResponse
from fastapi import HTTPException
import sys

def _base_dir() -> Path:
    # PyInstaller 打包运行时：资源会解压到 sys._MEIPASS
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    # 开发运行时：main.py 在 backend/app 里，往上两级到项目根目录 citecheck
    return Path(__file__).resolve().parents[2]

DIST_DIR = _base_dir() / "frontend" / "dist"

@app.get("/")
def spa_root():
    index = DIST_DIR / "index.html"
    if index.exists():
        return FileResponse(index)
    raise HTTPException(status_code=404, detail="Frontend not built. Run `npm run build` in frontend.")

@app.get("/{full_path:path}")
def spa_fallback(full_path: str):
    # 让 /login /register /assets/... 都能正确返回
    target = DIST_DIR / full_path
    if target.exists() and target.is_file():
        return FileResponse(target)
    index = DIST_DIR / "index.html"
    if index.exists():
        return FileResponse(index)
    raise HTTPException(status_code=404, detail="Frontend not built. Run `npm run build` in frontend.")