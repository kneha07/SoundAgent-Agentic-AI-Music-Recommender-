"""FastAPI backend for SoundAgent."""
import os
import sys
import uuid
from typing import Dict, List, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from src.recommender import load_songs, recommend_songs, UserProfile
from src.system import RecommendationAgent

# ── App ────────────────────────────────────────────────────────────────────────
app = FastAPI(title="SoundAgent API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── State ──────────────────────────────────────────────────────────────────────
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "songs.csv")
songs = load_songs(DATA_PATH)
agent = RecommendationAgent(songs)

# Simple in-memory session store {session_id: [history]}
sessions: Dict[str, List[Dict]] = {}

# ── Models ─────────────────────────────────────────────────────────────────────
class ProfileRequest(BaseModel):
    session_id: Optional[str] = None
    mood: str = "happy"
    energy: float = 0.7
    genre: str = "pop"
    vocal: str = "vocal"
    context: str = "general"
    decade: Optional[str] = None
    mood_tags: List[str] = []
    k: int = 5

class NLRequest(BaseModel):
    session_id: Optional[str] = None
    query: str
    k: int = 5

class SongOut(BaseModel):
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    score: float
    mood_tags: List[str] = []
    listening_context: str = "general"

class RecommendResponse(BaseModel):
    session_id: str
    songs: List[SongOut]
    explanation: Optional[str] = None
    confidence: Optional[float] = None
    mode: Optional[str] = None

# ── Helpers ────────────────────────────────────────────────────────────────────
def get_or_create_session(session_id: Optional[str]) -> str:
    sid = session_id or str(uuid.uuid4())
    if sid not in sessions:
        sessions[sid] = []
    return sid

# ── Routes ─────────────────────────────────────────────────────────────────────
@app.get("/api/health")
def health():
    return {"status": "ok", "songs": len(songs)}

@app.get("/api/catalog")
def catalog():
    genres = list({s.get("genre", "") for s in songs})
    moods = list({s.get("mood", "") for s in songs})
    contexts = list({s.get("listening_context", "") for s in songs})
    return {
        "total": len(songs),
        "genres": sorted(genres),
        "moods": sorted(moods),
        "contexts": sorted(contexts),
    }

@app.post("/api/recommend/profile", response_model=RecommendResponse)
def recommend_profile(req: ProfileRequest):
    sid = get_or_create_session(req.session_id)
    profile = UserProfile(
        favorite_genre=req.genre,
        favorite_mood=req.mood,
        target_energy=req.energy,
        likes_acoustic=False,
        vocal_preference=req.vocal,
        listening_context=req.context,
        preferred_decade=req.decade,
        desired_mood_tags=req.mood_tags,
    )
    results, scores = recommend_songs(songs, profile, k=req.k)
    out = [
        SongOut(
            title=s.get("title", ""),
            artist=s.get("artist", ""),
            genre=s.get("genre", ""),
            mood=s.get("mood", ""),
            energy=float(s.get("energy", 0)),
            score=round(float(sc), 3),
            mood_tags=[t.strip() for t in str(s.get("mood_tags", "")).split(",") if t.strip()],
            listening_context=s.get("listening_context", "general"),
        )
        for s, sc in zip(results, scores)
    ]
    sessions[sid].append({"type": "profile", "query": req.dict(), "results": [s.title for s in out]})
    return RecommendResponse(session_id=sid, songs=out)

@app.post("/api/recommend/nl", response_model=RecommendResponse)
def recommend_nl(req: NLRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    sid = get_or_create_session(req.session_id)
    result = agent.recommend_for_text(req.query, k=req.k)
    out = [
        SongOut(
            title=s.get("title", ""),
            artist=s.get("artist", ""),
            genre=s.get("genre", ""),
            mood=s.get("mood", ""),
            energy=float(s.get("energy", 0)),
            score=round(float(sc), 3),
            mood_tags=[t.strip() for t in str(s.get("mood_tags", "")).split(",") if t.strip()],
            listening_context=s.get("listening_context", "general"),
        )
        for s, sc, _ in result.recommendations
    ]
    sessions[sid].append({"type": "nl", "query": req.query, "results": [s.title for s in out]})
    return RecommendResponse(
        session_id=sid,
        songs=out,
        explanation=result.ai_explanation,
        confidence=result.confidence,
        mode=result.mode,
    )

@app.get("/api/session/{session_id}")
def get_session(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"session_id": session_id, "history": sessions[session_id]}

@app.delete("/api/session/{session_id}")
def clear_session(session_id: str):
    sessions.pop(session_id, None)
    return {"cleared": True}

# ── Serve React build ──────────────────────────────────────────────────────────
frontend_dist = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

    @app.get("/{full_path:path}")
    def serve_spa(full_path: str):
        return FileResponse(os.path.join(frontend_dist, "index.html"))
