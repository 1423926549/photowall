"""
PhotoWall Backend — Flask + Supabase (PostgreSQL) + Volcengine TOS
"""
import uuid
from datetime import date, datetime
from pathlib import Path

from flask import Flask, jsonify, request
from flask_cors import CORS
from psycopg2.pool import ThreadedConnectionPool
import tos

from config import (
    TOS_ACCESS_KEY, TOS_SECRET_KEY, TOS_ENDPOINT,
    TOS_REGION, TOS_BUCKET, SUPABASE_DATABASE_URL,
    LISTEN_HOST, LISTEN_PORT,
)

app = Flask(__name__)
CORS(app)

# ─────────────────────────────────────────
# TOS Client
# ─────────────────────────────────────────
tos_client = tos.TosClientV2(
    ak=TOS_ACCESS_KEY,
    sk=TOS_SECRET_KEY,
    endpoint=TOS_ENDPOINT,
    region=TOS_REGION,
)

# ─────────────────────────────────────────
# Supabase PostgreSQL (psycopg2)
# ─────────────────────────────────────────
_pool: ThreadedConnectionPool | None = None


def get_pool() -> ThreadedConnectionPool:
    global _pool
    if _pool is None:
        _pool = ThreadedConnectionPool(1, 10, SUPABASE_DATABASE_URL)
    return _pool


def get_conn():
    return get_pool().getconn()


def put_conn(conn):
    get_pool().putconn(conn)


# ─────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────
def _row_to_dict(row, cur) -> dict:
    cols = [desc[0] for desc in cur.description]
    return dict(zip(cols, row))


def _serialize(val):
    if isinstance(val, datetime):
        return val.isoformat()
    if isinstance(val, date):
        return val.strftime("%Y.%m.%d")
    return val


def _upload_to_tos(data: bytes, filename: str) -> tuple[str, str]:
    ext = Path(filename).suffix or ".jpg"
    key = f"photos/{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}{ext}"

    try:
        resp = tos_client.put_object(
            bucket=TOS_BUCKET,
            key=key,
            content=data,
        )
        if resp.status_code not in (200, 201):
            raise RuntimeError(f"TOS returned {resp.status_code}")
    except Exception as e:
        raise RuntimeError(f"TOS put_object error: {e}")

    return key, f"https://{TOS_BUCKET}.tos-cn-shanghai.volces.com/{key}"


def _delete_from_tos(key: str):
    try:
        tos_client.delete_object(bucket=TOS_BUCKET, key=key)
    except Exception:
        pass


# ─────────────────────────────────────────
# API Routes
# ─────────────────────────────────────────
@app.route("/api/photos", methods=["GET"])
def list_photos():
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, object_key, url, date, note, created_at "
                "FROM photos WHERE deleted = false ORDER BY date ASC"
            )
            rows = cur.fetchall()
            photos = [
                {k: _serialize(v) for k, v in _row_to_dict(row, cur).items()}
                for row in rows
            ]
        return jsonify(photos)
    finally:
        put_conn(conn)


@app.route("/api/photos", methods=["POST"])
def upload_photo():
    photo = request.files.get("photo")
    if not photo:
        return jsonify({"error": "No photo provided"}), 400

    data = photo.read()
    date_str = request.form.get("date", "") or datetime.now().strftime("%Y.%m.%d")
    note = request.form.get("note", "") or "美好的回忆"
    # Convert yyyy.MM.dd → yyyy-MM-dd for PostgreSQL DATE column
    date_val = date_str.replace(".", "-")

    try:
        key, url = _upload_to_tos(data, photo.filename or "photo.jpg")
    except Exception as e:
        return jsonify({"error": f"TOS upload failed: {e}"}), 500

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO photos (object_key, url, date, note) "
                "VALUES (%s, %s, %s, %s) RETURNING id",
                (key, url, date_val, note),
            )
            photo_id = cur.fetchone()[0]
        conn.commit()
    except Exception as e:
        _delete_from_tos(key)
        return jsonify({"error": f"DB insert failed: {e}"}), 500
    finally:
        put_conn(conn)

    return jsonify({
        "id": photo_id,
        "object_key": key,
        "url": url,
        "date": date_str,
        "note": note,
        "created_at": datetime.now().isoformat(),
    }), 201


@app.route("/api/photos/<int:photo_id>", methods=["PUT"])
def update_photo(photo_id):
    body = request.get_json(silent=True) or {}
    updates = {}
    if "date" in body and body["date"] is not None:
        updates["date"] = body["date"].replace(".", "-")
    if "note" in body and body["note"] is not None:
        updates["note"] = body["note"]
    if not updates:
        return jsonify({"status": "nothing to update"})

    set_clause = ", ".join(f"{k} = %s" for k in updates)
    values = list(updates.values()) + [photo_id]

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"UPDATE photos SET {set_clause} WHERE id = %s", values
            )
        conn.commit()
    finally:
        put_conn(conn)

    return jsonify({"status": "updated"})


@app.route("/api/photos/<int:photo_id>", methods=["DELETE"])
def delete_photo(photo_id):
    """Soft delete — only marks deleted=true."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM photos WHERE id = %s AND deleted = false",
                (photo_id,),
            )
            if not cur.fetchone():
                return jsonify({"error": "photo not found"}), 404

            cur.execute(
                "UPDATE photos SET deleted = true WHERE id = %s", (photo_id,)
            )
        conn.commit()
    finally:
        put_conn(conn)

    return jsonify({"status": "deleted"})


# ─────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────
if __name__ == "__main__":
    app.run(host=LISTEN_HOST, port=LISTEN_PORT, debug=True)
