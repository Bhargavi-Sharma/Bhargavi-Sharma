"""Web server: chart form, kundali view, full report and chat.

Run:  ANTHROPIC_API_KEY=sk-... uvicorn app:app --port 8000
"""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

from jyotish import dossier as dossier_mod
from jyotish.chart import BirthData, Chart

app = FastAPI(title="Jyotish Bot")
WEB = Path(__file__).parent / "web"
SESSIONS: dict[str, "object"] = {}


class ChartRequest(BaseModel):
    name: str = ""
    date: str              # YYYY-MM-DD
    time: str              # HH:MM or HH:MM:SS
    tz: str                # IANA zone or UTC offset like "5.5"
    lat: float
    lon: float
    place: str = ""
    gender: str = ""
    settings: dict | None = None


class ChatRequest(BaseModel):
    session_id: str
    message: str


@app.get("/")
def index():
    return FileResponse(WEB / "index.html")


@app.get("/api/status")
def status():
    return {"ai_enabled": bool(os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN"))}


@app.get("/api/geocode")
def geocode(q: str):
    url = "https://geocoding-api.open-meteo.com/v1/search?" + urlencode({"name": q, "count": 8, "language": "en"})
    try:
        with urlopen(url, timeout=10) as r:
            data = json.load(r)
    except OSError as e:
        raise HTTPException(502, f"geocoding failed: {e}")
    return [{"name": ", ".join(x for x in (g.get("name"), g.get("admin1"), g.get("country")) if x),
             "lat": g["latitude"], "lon": g["longitude"], "tz": g.get("timezone", "UTC")}
            for g in data.get("results", [])]


def _birth(req: ChartRequest) -> BirthData:
    try:
        tz: str | float = float(req.tz)
    except ValueError:
        tz = req.tz
    t = req.time if req.time.count(":") == 2 else req.time + ":00"
    return BirthData(req.name, datetime.fromisoformat(f"{req.date}T{t}"), tz, req.lat, req.lon, req.place,
                     req.gender.upper()[:1])


@app.post("/api/chart")
def chart(req: ChartRequest):
    try:
        birth = _birth(req)
        d = dossier_mod.build(birth, req.settings)
    except (ValueError, KeyError) as e:
        raise HTTPException(400, str(e))
    sid = None
    if status()["ai_enabled"]:
        from jyotish.bot import Session
        sid = uuid.uuid4().hex
        SESSIONS[sid] = Session(Chart(birth, req.settings), d)
    return json.loads(json.dumps({"session_id": sid, "dossier": d}, default=dossier_mod.serialise,
                                 ensure_ascii=False))


@app.post("/api/chat")
def chat(req: ChatRequest):
    sess = SESSIONS.get(req.session_id)
    if sess is None:
        raise HTTPException(404, "session not found - generate the chart again")

    def gen():
        try:
            for kind, data in sess.ask(req.message):
                yield f"data: {json.dumps({'type': kind, 'data': data}, ensure_ascii=False)}\n\n"
        except Exception as e:  # surface API errors to the UI
            yield f"data: {json.dumps({'type': 'error', 'data': str(e)})}\n\n"
        yield "data: {\"type\": \"done\"}\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")
