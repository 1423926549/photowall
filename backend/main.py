"""
PhotoWall Backend — FastAPI + SQLite + Volcengine TOS
"""
import uuid
import aiosqlite
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import tos

from config import (
    TOS_ACCESS_KEY, TOS_SECRET_KEY, TOS_ENDPOINT,
    TOS_REGION, TOS_BUCKET, DB_PATH, LISTEN_HOST, LISTEN_PORT,
)

app = FastAPI(title="PhotoWall API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────
# TOS Client (官方 SDK)
# ─────────────────────────────────────────
tos = tos.TosClientV2(
    ak=TOS_ACCESS_KEY,
    sk=TOS_SECRET_KEY,
    endpoint=TOS_ENDPOINT,
    region=TOS_REGION,
)

# ─────────────────────────────────────────
# SQLite
# ─────────────────────────────────────────
async def get_db() -> aiosqlite.Connection:
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    return db


async def init_db():
    db = await get_db()
    await db.execute("""
        CREATE TABLE IF NOT EXISTS photos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            object_key TEXT NOT NULL,
            url TEXT NOT NULL,
            date TEXT NOT NULL DEFAULT '',
            note TEXT NOT NULL DEFAULT '',
            deleted INTEGER NOT NULL DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now','localtime'))
        )
    """)
    # Migration: add deleted column if upgrading from old schema
    try:
        await db.execute("ALTER TABLE photos ADD COLUMN deleted INTEGER NOT NULL DEFAULT 0")
    except Exception:
        pass  # column already exists
    await db.commit()
    await db.close()


@app.on_event("startup")
async def startup():
    await init_db()
    print(f"[DB] SQLite initialized: {DB_PATH}")
    print(f"[TOS] Endpoint: {TOS_ENDPOINT}  Bucket: {TOS_BUCKET}")


# ─────────────────────────────────────────
# Models
# ─────────────────────────────────────────
class PhotoOut(BaseModel):
    id: int
    object_key: str
    url: str
    date: str
    note: str
    created_at: str


class PhotoUpdate(BaseModel):
    date: str | None = None
    note: str | None = None


# ─────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────
def upload_to_tos(data: bytes, filename: str) -> tuple[str, str]:
    """Upload to TOS, return (object_key, public_url)."""
    ext = Path(filename).suffix or ".jpg"
    key = f"photos/{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}{ext}"

    try:
        resp = tos.put_object(
            bucket=TOS_BUCKET,
            key=key,
            content=data,
        )
        if resp.status_code not in (200, 201):
            raise RuntimeError(f"TOS returned {resp.status_code}")
    except Exception as e:
        raise RuntimeError(f"TOS put_object error: {e}")

    # Public URL
    url = f"https://{TOS_BUCKET}.tos-cn-shanghai.volces.com/{key}"
    return key, url


def delete_from_tos(key: str):
    """Delete object from TOS."""
    try:
        tos.delete_object(bucket=TOS_BUCKET, key=key)
    except Exception:
        pass  # best-effort


# ─────────────────────────────────────────
# API Routes
# ─────────────────────────────────────────
@app.get("/api/photos")
async def list_photos():
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT id, object_key, url, date, note, created_at "
            "FROM photos WHERE deleted = 0 ORDER BY date ASC"
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]
    finally:
        await db.close()


@app.post("/api/photos", response_model=PhotoOut)
async def upload_photo(
    photo: UploadFile = File(...),
    date: str = Form(""),
    note: str = Form(""),
):
    data = await photo.read()

    # Upload to TOS
    try:
        key, url = upload_to_tos(data, photo.filename or "photo.jpg")
    except Exception as e:
        raise HTTPException(500, f"TOS upload failed: {e}")

    if not date:
        date = datetime.now().strftime("%Y.%m.%d")
    if not note:
        note = "美好的回忆"

    db = await get_db()
    try:
        cursor = await db.execute(
            "INSERT INTO photos (object_key, url, date, note) VALUES (?, ?, ?, ?)",
            (key, url, date, note),
        )
        await db.commit()
        photo_id = cursor.lastrowid
    except Exception as e:
        delete_from_tos(key)
        raise HTTPException(500, f"DB insert failed: {e}")
    finally:
        await db.close()

    return {
        "id": photo_id,
        "object_key": key,
        "url": url,
        "date": date,
        "note": note,
        "created_at": datetime.now().isoformat(),
    }


@app.put("/api/photos/{photo_id}")
async def update_photo(photo_id: int, body: PhotoUpdate):
    db = await get_db()
    try:
        fields = []
        values = []
        if body.date is not None:
            fields.append("date = ?")
            values.append(body.date)
        if body.note is not None:
            fields.append("note = ?")
            values.append(body.note)
        if not fields:
            return {"status": "nothing to update"}
        values.append(photo_id)
        await db.execute(f"UPDATE photos SET {', '.join(fields)} WHERE id = ?", values)
        await db.commit()
    finally:
        await db.close()
    return {"status": "updated"}


@app.delete("/api/photos/{photo_id}")
async def delete_photo(photo_id: int):
    """Soft delete — only marks deleted=1, does not touch TOS."""
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT id FROM photos WHERE id = ? AND deleted = 0", (photo_id,)
        )
        row = await cursor.fetchone()
        if not row:
            raise HTTPException(404, "photo not found")

        await db.execute("UPDATE photos SET deleted = 1 WHERE id = ?", (photo_id,))
        await db.commit()
    finally:
        await db.close()

    return {"status": "deleted"}


# ─────────────────────────────────────────
# Frontend static serving (production)
# ─────────────────────────────────────────
frontend_dir = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")


# ─────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=LISTEN_HOST, port=LISTEN_PORT, reload=True)
