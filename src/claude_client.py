"""Claude API integration for mood parsing and recommendation explanation."""

import logging
from typing import List, Literal, Optional

import anthropic
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

_client: Optional[anthropic.Anthropic] = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic()
    return _client


_PARSE_SYSTEM = """You are a music preference parser for a recommendation system. Extract structured preferences from a natural language request.

Mood mappings: nostalgic/melancholic/sad/down→sad, energetic/upbeat/joyful/excited→happy, calm/peaceful/mellow→chill, angry/aggressive/hard→intense, focused/productive/concentrated→focused.

Energy scale 0.0–1.0:
  sleep/ambient/soft/wind-down → 0.10–0.30
  study/coffee/relax → 0.25–0.45
  moderate/balanced → 0.50–0.65
  upbeat/dance/party → 0.70–0.85
  workout/intense/pump-up/driving → 0.85–0.95

target_popularity: 85=chart hits, 70=mainstream, 55=indie/underground.

desired_mood_tags must only use: euphoric, bright, dreamy, aggressive, powerful, mellow, emotional, festive, cozy, warm, smooth, cosmic, nostalgic."""


class MoodPreferences(BaseModel):
    mood: Literal["happy", "sad", "chill", "relaxed", "intense", "focused", "moody"]
    energy: float
    acoustic_preference: Literal["acoustic", "electronic", "mixed"]
    favorite_genre: Optional[str] = None
    listening_context: Optional[str] = None
    preferred_decade: Optional[Literal["1990s", "2000s", "2010s", "2020s"]] = None
    target_popularity: int
    vocal_preference: Literal["vocal", "instrumental"]
    desired_mood_tags: List[str] = Field(default_factory=list)


def parse_mood_input(request: str) -> dict:
    """Parse natural language mood description into structured music preferences."""
    client = _get_client()
    response = client.messages.parse(
        model="claude-opus-4-7",
        max_tokens=512,
        system=[{
            "type": "text",
            "text": _PARSE_SYSTEM,
            "cache_control": {"type": "ephemeral"},
        }],
        messages=[{"role": "user", "content": request}],
        output_format=MoodPreferences,
    )
    p = response.parsed_output
    return {
        "mood": p.mood,
        "energy": p.energy,
        "acoustic_preference": p.acoustic_preference,
        "favorite_genre": p.favorite_genre,
        "listening_context": p.listening_context,
        "preferred_decade": p.preferred_decade,
        "target_popularity": p.target_popularity,
        "vocal_preference": p.vocal_preference,
        "desired_mood_tags": p.desired_mood_tags,
    }


_EXPLAIN_SYSTEM = """You are a music recommendation assistant. Given a user's listening request and the songs recommended for them, write a warm, specific explanation (2–3 sentences) of why these songs match what they asked for. Reference the mood, energy, genre, and context they described. Be conversational and enthusiastic."""


def generate_recommendation_explanation(
    request: str,
    recommendations: list,
    user_prefs: dict,
) -> str:
    """Generate a natural language explanation for the recommendations using Claude."""
    client = _get_client()

    top_songs = []
    for i, (song, score, _) in enumerate(recommendations[:3], 1):
        top_songs.append(
            f'{i}. "{song["title"]}" by {song["artist"]} '
            f'({song["genre"]}, {song["mood"]} mood, score {score:.2f})'
        )

    user_msg = (
        f'User request: "{request}"\n\n'
        f'Top recommended songs:\n' + "\n".join(top_songs)
    )

    with client.messages.stream(
        model="claude-opus-4-7",
        max_tokens=256,
        system=[{
            "type": "text",
            "text": _EXPLAIN_SYSTEM,
            "cache_control": {"type": "ephemeral"},
        }],
        messages=[{"role": "user", "content": user_msg}],
    ) as stream:
        final = stream.get_final_message()
        text_blocks = [b for b in final.content if b.type == "text"]
        return text_blocks[0].text if text_blocks else ""
