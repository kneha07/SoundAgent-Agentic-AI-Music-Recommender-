import csv
import logging
import os
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from .recommender import recommend_songs
from .claude_client import generate_recommendation_explanation, parse_mood_input

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

MOOD_KEYWORDS = {
    'happy': 'happy',
    'sad': 'sad',
    'chill': 'chill',
    'relaxed': 'relaxed',
    'intense': 'intense',
    'focused': 'focused',
    'moody': 'moody',
    'energetic': 'happy',
    'melancholy': 'sad',
}

CONTEXT_KEYWORDS = {
    'study': 'study',
    'workout': 'workout',
    'party': 'party',
    'relax': 'relax',
    'coffee': 'coffee',
    'night': 'night',
    'drive': 'drive',
    'beach': 'beach',
    'sleep': 'relax',
}

GENRE_KEYWORDS = {
    'pop': 'pop',
    'lofi': 'lofi',
    'rock': 'rock',
    'jazz': 'jazz',
    'house': 'house',
    'synthwave': 'synthwave',
    'indie': 'indie',
    'ambient': 'ambient',
    'metal': 'metal',
    'r&b': 'r&b',
    'latin': 'latin',
    'blues': 'blues',
    'folk': 'folk',
    'reggae': 'reggae',
}

DECADE_KEYWORDS = {
    '1990s': '1990s',
    '2000s': '2000s',
    '2010s': '2010s',
    '2020s': '2020s',
}

MUSIC_KEYWORDS = {
    'acoustic': 'acoustic',
    'electric': 'electronic',
    'electronic': 'electronic',
    'vocal': 'vocal',
    'instrumental': 'instrumental',
    'dreamy': 'dreamy',
    'bright': 'bright',
    'emotional': 'emotional',
    'energetic': 'energetic',
}

ENERGY_HINTS = {
    'high energy': 0.95,
    'low energy': 0.20,
    'energy': 0.60,
    'intense': 0.90,
    'chill': 0.35,
    'relaxed': 0.40,
    'soft': 0.35,
    'upbeat': 0.85,
    'slow': 0.30,
}

SPECIALIZED_PROFILE_KEYWORDS = {
    'study': ['study', 'focus', 'coffee', 'calm', 'productivity', 'work'],
    'party': ['party', 'dance', 'festival', 'bright', 'euphoric', 'upbeat'],
    'workout': ['workout', 'gym', 'exercise', 'pump', 'energetic', 'powerful'],
    'relax': ['relax', 'wind down', 'chill', 'mellow', 'sleep', 'rest'],
    'night': ['night', 'midnight', 'late', 'nocturnal', 'emotional'],
}

TONE_KEYWORDS = {
    'company': 'company',
    'corporate': 'company',
    'business': 'company',
    'professional': 'company',
    'friendly': 'friendly',
    'casual': 'casual',
    'warm': 'friendly',
}

@dataclass
class RecommendationResult:
    request: str
    user_prefs: Dict
    mode: str
    recommendations: List[Tuple[Dict, float, str]]
    confidence: float
    notes: List[str]
    retrieved_docs: Optional[List[Dict]] = None
    specialized_profile: Optional[str] = None
    response_tone: Optional[str] = None
    ai_explanation: Optional[str] = None


class RecommendationAgent:
    """Agentic interface for the music recommender system."""

    def __init__(self, songs: List[Dict], extra_documents: Optional[List[Dict]] = None):
        self.songs = songs
        self.extra_documents = extra_documents or self.load_extra_documents()

    def load_extra_documents(self) -> List[Dict]:
        base_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'genre_notes.csv')
        extra_docs: List[Dict] = []
        if not os.path.exists(base_path):
            return extra_docs

        with open(base_path, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                genre = row.get('genre', '').strip()
                description = row.get('description', '').strip()
                if not genre or not description:
                    continue
                extra_docs.append({
                    'type': 'genre_note',
                    'genre': genre,
                    'description': description,
                    'doc_text': f"Genre {genre}: {description}",
                })
        return extra_docs

    def parse_request(self, request: str) -> Dict:
        text = request.lower()

        # Keyword-based fallback parsing
        mood = 'happy'
        for keyword, mapped in MOOD_KEYWORDS.items():
            if keyword in text:
                mood = mapped
                break

        acoustic_preference = 'mixed'
        if 'acoustic' in text or 'unplugged' in text:
            acoustic_preference = 'acoustic'
        elif 'electronic' in text or 'electro' in text or 'synth' in text:
            acoustic_preference = 'electronic'

        preferred_genre = None
        for keyword, mapped in GENRE_KEYWORDS.items():
            if keyword in text:
                preferred_genre = mapped
                break

        listening_context = None
        for keyword, mapped in CONTEXT_KEYWORDS.items():
            if keyword in text:
                listening_context = mapped
                break

        preferred_decade = None
        for keyword, mapped in DECADE_KEYWORDS.items():
            if keyword in text:
                preferred_decade = mapped
                break

        target_popularity = 70
        if 'popular' in text or 'hit' in text or 'top' in text:
            target_popularity = 80
        elif 'underground' in text or 'indie' in text:
            target_popularity = 55

        energy = 0.60
        for keyword, value in ENERGY_HINTS.items():
            if keyword in text:
                energy = value
                break

        vocal_preference = 'vocal'
        if 'instrumental' in text or 'without vocals' in text:
            vocal_preference = 'instrumental'

        desired_mood_tags = []
        for keyword in ['dreamy', 'bright', 'aggressive', 'powerful', 'mellow', 'euphoric', 'nostalgic', 'emotional', 'festive', 'cozy', 'warm', 'smooth', 'cosmic']:
            if keyword in text:
                desired_mood_tags.append(keyword)

        # Override with Claude's deeper NLU when the API key is available
        try:
            claude_prefs = parse_mood_input(request)
            mood = claude_prefs.get('mood', mood)
            energy = claude_prefs.get('energy', energy)
            acoustic_preference = claude_prefs.get('acoustic_preference', acoustic_preference)
            preferred_genre = claude_prefs.get('favorite_genre', preferred_genre)
            listening_context = claude_prefs.get('listening_context', listening_context)
            preferred_decade = claude_prefs.get('preferred_decade', preferred_decade)
            target_popularity = claude_prefs.get('target_popularity', target_popularity)
            vocal_preference = claude_prefs.get('vocal_preference', vocal_preference)
            desired_mood_tags = claude_prefs.get('desired_mood_tags', desired_mood_tags)
        except Exception as e:
            logger.warning('Claude parsing unavailable, using keyword matching: %s', e)

        mode = 'balanced'
        if preferred_genre:
            mode = 'genre-first'
        elif mood in ['happy', 'sad', 'chill']:
            mode = 'mood-first'

        if 'energy-first' in text or 'high-energy' in text or 'pumped' in text:
            mode = 'energy-first'

        specialized_profile = None
        for profile, keywords in SPECIALIZED_PROFILE_KEYWORDS.items():
            if any(keyword in text for keyword in keywords):
                specialized_profile = profile
                break

        response_tone = None
        for keyword, tone in TONE_KEYWORDS.items():
            if keyword in text:
                response_tone = tone
                break

        return {
            'mood': mood,
            'energy': energy,
            'acoustic_preference': acoustic_preference,
            'favorite_genre': preferred_genre,
            'target_popularity': target_popularity,
            'preferred_decade': preferred_decade,
            'desired_mood_tags': desired_mood_tags,
            'vocal_preference': vocal_preference,
            'listening_context': listening_context,
            'mode': mode,
            'specialized_profile': specialized_profile,
            'response_tone': response_tone,
        }

    def retrieve_relevant_documents(self, request: str, limit: int = 5) -> List[Dict]:
        text = request.lower()
        keywords = set(re.findall(r"[a-z0-9]+", text))

        scored: List[Dict] = []
        for song in self.songs:
            score = 0.0
            if song['mood'] in keywords:
                score += 2.0
            if song['genre'] in keywords:
                score += 1.5
            if song['listening_context'] in keywords:
                score += 1.5
            if any(tag in keywords for tag in song['mood_tags']):
                score += 1.0
            if any(word in song['title'].lower() for word in keywords):
                score += 0.8
            if any(word in song['artist'].lower() for word in keywords):
                score += 0.5
            if song['release_decade'] in keywords:
                score += 0.7

            doc_text = (
                f"{song['title']} by {song['artist']} is a {song['genre']} track with mood {song['mood']}, "
                f"tags {', '.join(song['mood_tags'])}, context {song['listening_context']}.")
            scored.append({'song': song, 'score': score, 'doc_text': doc_text, 'source': 'song'})

        for extra in self.extra_documents:
            score = 0.0
            text_lower = extra['doc_text'].lower()
            if any(keyword in text_lower for keyword in keywords):
                score += 1.0
            if extra.get('genre') and extra['genre'] in keywords:
                score += 1.5
            if score > 0:
                scored.append({'song': None, 'score': score, 'doc_text': extra['doc_text'], 'source': 'external', 'genre': extra.get('genre')})

        scored.sort(key=lambda item: item['score'], reverse=True)
        selected = [item for item in scored if item['score'] > 0][:limit]
        if not selected:
            logger.warning('No retrieval keywords matched; falling back to full catalog')
            selected = [
                {
                    'song': song,
                    'score': 0.0,
                    'doc_text': f"{song['title']} by {song['artist']}",
                    'source': 'song'
                }
                for song in self.songs[:limit]
            ]
        return selected

    def retrieve_relevant_songs(self, request: str, limit: int = 15) -> List[Dict]:
        docs = self.retrieve_relevant_documents(request, limit=5)
        candidates: List[Dict] = []
        candidate_ids = set()
        for doc in docs:
            song = doc['song']
            if song and song['id'] not in candidate_ids:
                candidates.append(song)
                candidate_ids.add(song['id'])

        for doc in docs:
            if doc['source'] == 'external' and doc.get('genre'):
                for song in self.songs:
                    if song['genre'] == doc['genre'] and song['id'] not in candidate_ids:
                        candidates.append(song)
                        candidate_ids.add(song['id'])
                        if len(candidates) >= limit:
                            break
                if len(candidates) >= limit:
                    break

        for song in self.songs:
            if len(candidates) >= limit:
                break
            if song['id'] not in candidate_ids:
                candidates.append(song)
                candidate_ids.add(song['id'])

        return candidates[:limit]

    def compute_confidence(self, result: RecommendationResult) -> float:
        if not result.recommendations:
            return 0.0

        requested_mood = result.user_prefs.get('mood')
        requested_context = result.user_prefs.get('listening_context')
        requested_genre = result.user_prefs.get('favorite_genre')

        matches = 0
        for song, _, _ in result.recommendations[:3]:
            if requested_mood and song['mood'] == requested_mood:
                matches += 1
            if requested_context and song['listening_context'] == requested_context:
                matches += 1
            if requested_genre and song['genre'] == requested_genre:
                matches += 1

        raw = matches / max(1, 3 * 3)
        return round(max(0.25, min(1.0, 0.4 + raw * 0.6)), 2)

    def validate_recommendations(self, request: str, result: RecommendationResult) -> RecommendationResult:
        requested_mood = result.user_prefs.get('mood')
        requested_context = result.user_prefs.get('listening_context')
        if not result.recommendations:
            result.notes.append('No recommendations could be generated.')
            return result

        top_song = result.recommendations[0][0]
        if requested_mood and top_song['mood'] != requested_mood:
            result.notes.append('Top song mood does not exactly match request; trying mood-first fallback.')
            fallback_prefs = {**result.user_prefs, 'mode': 'mood-first'}
            fallback_recs = recommend_songs(fallback_prefs, self.retrieve_relevant_songs(request, limit=15), k=len(result.recommendations), mode='mood-first')
            result.recommendations = fallback_recs
            result.confidence = self.compute_confidence(result)

        if requested_context and all(song['listening_context'] != requested_context for song, _, _ in result.recommendations[:3]):
            result.notes.append('Context not well represented in top songs; including broader candidates.')
            broader_recs = recommend_songs(result.user_prefs, self.songs, k=len(result.recommendations), mode=result.mode)
            result.recommendations = broader_recs
            result.confidence = self.compute_confidence(result)

        return result

    def recommend_for_text(self, request: str, k: int = 5) -> RecommendationResult:
        user_prefs = self.parse_request(request)
        retrieved_docs = self.retrieve_relevant_documents(request, limit=5)
        candidate_songs = self.retrieve_relevant_songs(request, limit=15)
        recommendations = recommend_songs(
            user_prefs,
            candidate_songs,
            k=k,
            mode=user_prefs.get('mode', 'balanced'),
            specialized_profile=user_prefs.get('specialized_profile'),
        )
        result = RecommendationResult(
            request=request,
            user_prefs=user_prefs,
            mode=user_prefs.get('mode', 'balanced'),
            recommendations=recommendations,
            confidence=0.0,
            notes=[f"Retrieved {len(candidate_songs)} candidate songs."],
            retrieved_docs=retrieved_docs,
            specialized_profile=user_prefs.get('specialized_profile'),
            response_tone=user_prefs.get('response_tone'),
        )
        result.confidence = self.compute_confidence(result)
        result = self.validate_recommendations(request, result)

        try:
            result.ai_explanation = generate_recommendation_explanation(
                request, result.recommendations, user_prefs
            )
        except Exception as e:
            logger.warning('Claude explanation unavailable: %s', e)

        return result

    def apply_response_tone(self, lines: List[str], tone: Optional[str]) -> List[str]:
        if tone == 'company':
            lines.insert(0, 'Recommendation generated in a professional, business-friendly tone.')
        elif tone == 'friendly':
            lines.insert(0, 'Here is a friendly and warm music recommendation set for you:')
        elif tone == 'casual':
            lines.insert(0, 'Here are some easygoing picks to match your vibe:')
        return lines

    def format_result(self, result: RecommendationResult) -> str:
        lines = [f'Request: {result.request}', f'Mode: {result.mode}', f'Confidence: {result.confidence:.2f}']
        if result.response_tone:
            lines.append(f'Response tone: {result.response_tone}')
        lines.append('Preferences:')
        for key in ['mood', 'energy', 'acoustic_preference', 'favorite_genre', 'preferred_decade', 'desired_mood_tags', 'vocal_preference', 'listening_context']:
            value = result.user_prefs.get(key)
            if value:
                lines.append(f'  - {key}: {value}')
        lines.append('\nTop recommendations:')
        for rank, (song, score, explanation) in enumerate(result.recommendations, start=1):
            lines.append(f'{rank}. {song["title"]} by {song["artist"]} ({song["genre"]}, {song["mood"]}) - {score:.3f}')
            lines.append(f'   • context: {song["listening_context"]}, mood_tags: {", ".join(song["mood_tags"])}')
        if result.retrieved_docs:
            lines.append('\nRetrieved Documents:')
            for doc in result.retrieved_docs:
                lines.append(f'  - {doc["song"]["title"]} ({doc["song"]["genre"]}, score {doc["score"]:.2f})')
                lines.append(f'    • {doc["doc_text"]}')
        if result.notes:
            lines.append('\nNotes:')
            for note in result.notes:
                lines.append(f'  - {note}')
        lines = self.apply_response_tone(lines, result.response_tone)
        return '\n'.join(lines)


def build_sample_requests() -> List[str]:
    return [
        'Recommend upbeat party music for a happy listener who loves electronic pop and bright energy.',
        'I want calm study songs with a chill mood and dreamy textures for coffee work.',
        'Give me intense workout tracks with strong rock or pop energy and aggressive mood tags.',
        'Find sad but powerful night music that is emotional and vocal-heavy.',
    ]
