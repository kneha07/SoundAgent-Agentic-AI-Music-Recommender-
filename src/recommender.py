from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
import csv

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    popularity: int = 70
    release_decade: str = "2020s"
    mood_tags: List[str] = field(default_factory=list)
    instrumentalness: float = 0.0
    speechiness: float = 0.0
    listening_context: str = "general"

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    target_popularity: int = 70
    preferred_decade: str = None
    desired_mood_tags: List[str] = field(default_factory=list)
    vocal_preference: str = "vocal"
    listening_context: str = None

# Shared scoring constants — used by both Recommender class and recommend_songs function.
# Override dicts intentionally list only the features being adjusted; unspecified features
# retain their default values and the full dict is renormalized to 1.0.
# Use resolve_weights() to inspect the final effective weights for any combination.
DEFAULT_WEIGHTS: Dict[str, float] = {
    'energy': 0.15,
    'mood': 0.12,
    'genre': 0.11,
    'acousticness': 0.09,
    'danceability': 0.09,
    'valence': 0.07,
    'popularity': 0.08,
    'release_decade': 0.06,
    'mood_tags': 0.08,
    'instrumentalness': 0.06,
    'speechiness': 0.05,
    'listening_context': 0.04,
}

MODE_WEIGHT_OVERRIDES: Dict[str, Dict[str, float]] = {
    'balanced': {},
    'mood-first': {
        'mood': 0.16,
        'mood_tags': 0.12,
        'valence': 0.11,
        'energy': 0.14,
        'genre': 0.10,
        'release_decade': 0.05,
        'listening_context': 0.05,
    },
    'genre-first': {
        'genre': 0.18,
        'mood': 0.13,
        'energy': 0.13,
        'popularity': 0.10,
        'acousticness': 0.08,
        'danceability': 0.08,
        'valence': 0.07,
        'mood_tags': 0.07,
        'release_decade': 0.05,
        'listening_context': 0.05,
    },
    'energy-first': {
        'energy': 0.22,
        'danceability': 0.14,
        'genre': 0.09,
        'mood': 0.11,
        'acousticness': 0.08,
        'popularity': 0.08,
        'mood_tags': 0.08,
        'valence': 0.08,
        'instrumentalness': 0.06,
        'speechiness': 0.05,
    },
}

SPECIALIZED_PROFILE_OVERRIDES: Dict[str, Dict[str, float]] = {
    'study': {
        'acousticness': 0.16,
        'mood_tags': 0.14,
        'listening_context': 0.10,
        'energy': 0.10,
        'danceability': 0.09,
        'valence': 0.08,
        'genre': 0.08,
        'release_decade': 0.06,
    },
    'party': {
        'energy': 0.18,
        'danceability': 0.16,
        'genre': 0.10,
        'mood': 0.12,
        'mood_tags': 0.10,
        'popularity': 0.10,
        'acousticness': 0.06,
        'speechiness': 0.06,
        'release_decade': 0.06,
    },
    'workout': {
        'energy': 0.20,
        'danceability': 0.14,
        'genre': 0.09,
        'mood': 0.10,
        'popularity': 0.10,
        'instrumentalness': 0.06,
        'speechiness': 0.06,
        'mood_tags': 0.08,
        'acousticness': 0.07,
        'release_decade': 0.06,
    },
    'relax': {
        'acousticness': 0.16,
        'valence': 0.14,
        'mood': 0.11,
        'mood_tags': 0.10,
        'genre': 0.09,
        'energy': 0.07,
        'release_decade': 0.08,
        'instrumentalness': 0.08,
        'speechiness': 0.05,
        'listening_context': 0.06,
    },
}


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Dict]):
        self.songs = songs
        self.default_weights = DEFAULT_WEIGHTS
        self.mode_weight_overrides = MODE_WEIGHT_OVERRIDES
        self.specialized_profile_overrides = SPECIALIZED_PROFILE_OVERRIDES

    def recommend(self, user_prefs: Dict, k: int = 5, mode: str = "balanced", specialized_profile: Optional[str] = None, weight_overrides: Optional[Dict[str, float]] = None) -> List[Tuple[Dict, float, str]]:
        """Return top-k song recommendations for user using weighted proximity scoring."""
        """Return top-k song recommendations for user using weighted proximity scoring."""
        # Resolve weights
        final_overrides = {**self.mode_weight_overrides.get(mode, {}), **(weight_overrides or {})}
        if specialized_profile:
            final_overrides = {**final_overrides, **self.specialized_profile_overrides.get(specialized_profile, {})}
        weights = {**self.default_weights, **final_overrides}
        total_weight = sum(weights.values())
        if abs(total_weight - 1.0) > 1e-9:
            weights = {feature: weight / total_weight for feature, weight in weights.items()}

        scored_songs = [
            (song, self._score_song(user_prefs, song, weights), self.explain_recommendation(user_prefs, song))
            for song in self.songs
        ]
        # Sort by score descending, return top k
        top_songs = sorted(scored_songs, key=lambda x: x[1], reverse=True)
        return top_songs[:k]

    def _score_song(self, user_prefs: Dict, song: Dict, weights: Dict[str, float]) -> float:
        """Compute 12-feature weighted recommendation score for song given user profile (0.0-1.0)."""
        
        score = 0.0
        
        # Energy
        energy_diff = abs(song['energy'] - user_prefs.get('energy', 0.5))
        energy_score = max(0.0, 1.0 - energy_diff)
        score += weights['energy'] * energy_score
        
        # Mood
        mood_match = song['mood'] == user_prefs.get('mood', 'happy')
        mood_score = 1.0 if mood_match else 0.5
        score += weights['mood'] * mood_score
        
        # Genre
        genre_score = 1.0 if user_prefs.get('favorite_genre') and song['genre'] == user_prefs.get('favorite_genre') else 0.5
        score += weights['genre'] * genre_score
        
        # Acousticness
        likes_acoustic = user_prefs.get('acoustic_preference', 'mixed') == 'acoustic'
        if likes_acoustic:
            acousticness_score = song['acousticness']
        else:
            acousticness_score = 1.0 - song['acousticness']
        score += weights['acousticness'] * acousticness_score
        
        # Danceability
        if song['mood'] in ['happy', 'intense']:
            danceability_score = song['danceability']
        else:
            danceability_score = 0.5
        score += weights['danceability'] * danceability_score
        
        # Valence
        favorite_mood = user_prefs.get('mood', 'happy')
        if favorite_mood == 'happy':
            valence_score = song['valence']
        elif favorite_mood in ['chill', 'relaxed']:
            valence_score = 1.0 - song['valence']
        else:
            valence_score = 0.5
        score += weights['valence'] * valence_score
        
        # Popularity
        target_popularity = user_prefs.get('target_popularity', 70)
        popularity_diff = abs(song['popularity'] - target_popularity) / 100.0
        popularity_score = max(0.0, 1.0 - popularity_diff)
        score += weights['popularity'] * popularity_score
        
        # Release Decade
        preferred_decade = user_prefs.get('preferred_decade')
        decade_score = 1.0 if preferred_decade and song['release_decade'] == preferred_decade else 0.5
        score += weights['release_decade'] * decade_score
        
        # Mood Tags
        desired_mood_tags = user_prefs.get('desired_mood_tags', [])
        if desired_mood_tags and song['mood_tags']:
            tag_matches = sum(1 for tag in desired_mood_tags if tag in song['mood_tags'])
            mood_tag_score = min(1.0, tag_matches / len(desired_mood_tags))
        else:
            mood_tag_score = 0.5
        score += weights['mood_tags'] * mood_tag_score
        
        # Instrumentalness and Speechiness
        vocal_preference = user_prefs.get('vocal_preference', 'vocal')
        if vocal_preference == 'instrumental':
            instrumentalness_score = song['instrumentalness']
            speechiness_score = 1.0 - song['speechiness']
        else:
            instrumentalness_score = 1.0 - song['instrumentalness']
            speechiness_score = song['speechiness']
        score += weights['instrumentalness'] * instrumentalness_score
        score += weights['speechiness'] * speechiness_score
        
        # Listening Context
        listening_context = user_prefs.get('listening_context')
        if listening_context:
            context_score = 1.0 if song['listening_context'] == listening_context else 0.5
            score += weights['listening_context'] * context_score
        
        return score

    def explain_recommendation(self, user_prefs: Dict, song: Dict) -> str:
        """Generate human-readable explanation of why this song was recommended."""
        reasons = []
        
        # Energy explanation
        energy_diff = abs(song['energy'] - user_prefs.get('energy', 0.5))
        if energy_diff < 0.2:
            reasons.append(f"energy level matches your preference ({song['energy']:.1f})")
        
        # Mood explanation
        if song['mood'] == user_prefs.get('mood', 'happy'):
            reasons.append(f"perfect {song['mood']} mood match")
        
        # Acousticness explanation
        likes_acoustic = user_prefs.get('acoustic_preference', 'mixed') == 'acoustic'
        if likes_acoustic and song['acousticness'] > 0.6:
            reasons.append("has that acoustic vibe you enjoy")
        elif not likes_acoustic and song['acousticness'] < 0.3:
            reasons.append("features electronic production you prefer")
        
        # Danceability explanation
        if song['danceability'] > 0.75:
            reasons.append("very danceable")
        
        # Genre explanation
        if song['genre'] == user_prefs.get('favorite_genre'):
            reasons.append(f"in your favorite genre ({song['genre']})")
        
        if not reasons:
            reasons.append("fits your music taste profile")
        
        return "This song was recommended because it " + ", and ".join(reasons)

def load_songs(csv_path: str) -> List[Dict]:
    """Load song dictionaries from CSV with numeric type conversion and advanced attributes."""
    print(f"Loading songs from {csv_path}...")
    songs = []

    try:
        with open(csv_path, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                mood_tags = [tag.strip() for tag in row['mood_tags'].split(';') if tag.strip()]
                song_dict = {
                    'id': int(row['id']),
                    'title': row['title'],
                    'artist': row['artist'],
                    'genre': row['genre'],
                    'mood': row['mood'],
                    'energy': float(row['energy']),
                    'tempo_bpm': float(row['tempo_bpm']),
                    'valence': float(row['valence']),
                    'danceability': float(row['danceability']),
                    'acousticness': float(row['acousticness']),
                    'popularity': int(row['popularity']),
                    'release_decade': row['release_decade'],
                    'mood_tags': mood_tags,
                    'instrumentalness': float(row['instrumentalness']),
                    'speechiness': float(row['speechiness']),
                    'listening_context': row['listening_context'],
                }
                songs.append(song_dict)
        print(f"✓ Loaded {len(songs)} songs")
    except FileNotFoundError:
        print(f"✗ Error: Could not find file at {csv_path}")

    return songs


def resolve_weights(
    default_weights: Dict[str, float],
    mode_overrides: Optional[Dict[str, float]] = None,
    profile_overrides: Optional[Dict[str, float]] = None,
) -> Dict[str, float]:
    """
    Resolve final effective weights after applying mode and specialized profile overrides.

    This helper clarifies what the actual normalized weights will be for any combination of
    mode and specialized profile. Useful for debugging weight assignment logic.

    Args:
        default_weights: Base weight dictionary
        mode_overrides: Mode-specific weight overrides (e.g., 'mood-first' overrides)
        profile_overrides: Specialized profile overrides (e.g., 'study' profile)

    Returns:
        Final normalized weight dictionary (sums to 1.0)

    Example:
        >>> defaults = {'energy': 0.15, 'mood': 0.12, ...}
        >>> mood_first = {'mood': 0.16, 'mood_tags': 0.12, ...}
        >>> final = resolve_weights(defaults, mood_first)
        >>> sum(final.values())  # == 1.0
    """
    weights = {**default_weights}

    if mode_overrides:
        weights.update(mode_overrides)
    if profile_overrides:
        weights.update(profile_overrides)

    # Renormalize to sum to exactly 1.0
    total_weight = sum(weights.values())
    if abs(total_weight - 1.0) > 1e-9:
        weights = {feature: weight / total_weight for feature, weight in weights.items()}

    return weights


def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    ignore_mood: bool = False,
    mode: str = "balanced",
    specialized_profile: Optional[str] = None,
    weight_overrides: Optional[Dict[str, float]] = None,
) -> List[Tuple[Dict, float, str]]:
    """Generate top-k recommendations with scoring modes and diversity penalty."""
    default_weights = DEFAULT_WEIGHTS
    mode_weight_overrides = MODE_WEIGHT_OVERRIDES
    specialized_profile_overrides = SPECIALIZED_PROFILE_OVERRIDES

    # Weight resolution: Merge mode and profile overrides, then renormalize.
    # IMPORTANT: When an override dict specifies only some features, the unspecified
    # features retain their previous values (from default_weights or mode_weights).
    # The entire dict is then renormalized so all weights sum to 1.0.
    # To inspect final effective weights, call resolve_weights() helper.
    final_overrides = {**mode_weight_overrides.get(mode, {}), **(weight_overrides or {})}
    if specialized_profile:
        final_overrides = {**final_overrides, **specialized_profile_overrides.get(specialized_profile, {})}
    weights = {**default_weights, **final_overrides}
    total_weight = sum(weights.values())
    if abs(total_weight - 1.0) > 1e-9:
        weights = {feature: weight / total_weight for feature, weight in weights.items()}


    def score_song(song: Dict, prefs: Dict) -> Tuple[float, List[str]]:
        score = 0.0
        reasons = []

        target_mood = prefs.get('mood', 'happy')
        target_energy = prefs.get('energy', 0.5)
        likes_acoustic = prefs.get('acoustic_preference', 'mixed') == 'acoustic'
        favorite_genre = prefs.get('favorite_genre')
        target_popularity = prefs.get('target_popularity', 70)
        preferred_decade = prefs.get('preferred_decade')
        desired_mood_tags = prefs.get('desired_mood_tags', [])
        vocal_preference = prefs.get('vocal_preference', 'vocal')
        listening_context = prefs.get('listening_context')

        energy_diff = abs(song['energy'] - target_energy)
        energy_score = max(0.0, 1.0 - energy_diff)
        energy_contribution = weights['energy'] * energy_score
        score += energy_contribution
        reasons.append(
            f"Energy: {energy_score:.2f} × {weights['energy']:.2f} = +{energy_contribution:.3f} ({song['energy']:.2f} vs {target_energy:.2f})"
        )

        if ignore_mood:
            mood_score = 0.50
            mood_status = 'ignored'
        else:
            mood_match = song['mood'] == target_mood
            mood_score = 1.0 if mood_match else 0.5
            mood_status = 'exact match' if mood_match else 'partial match'
        mood_contribution = weights['mood'] * mood_score
        score += mood_contribution
        reasons.append(
            f"Mood: {mood_score:.2f} × {weights['mood']:.2f} = +{mood_contribution:.3f} ({mood_status})"
        )

        genre_score = 1.0 if favorite_genre and song['genre'] == favorite_genre else 0.5
        genre_context = 'favorite genre match' if favorite_genre and song['genre'] == favorite_genre else 'genre similarity'
        genre_contribution = weights['genre'] * genre_score
        score += genre_contribution
        reasons.append(
            f"Genre: {genre_score:.2f} × {weights['genre']:.2f} = +{genre_contribution:.3f} ({genre_context})"
        )

        if likes_acoustic:
            acousticness_score = song['acousticness']
            acoustic_pref = 'likes acoustic'
        else:
            acousticness_score = 1.0 - song['acousticness']
            acoustic_pref = 'likes electronic'
        acousticness_contribution = weights['acousticness'] * acousticness_score
        score += acousticness_contribution
        reasons.append(
            f"Acousticness: {acousticness_score:.2f} × {weights['acousticness']:.2f} = +{acousticness_contribution:.3f} ({acoustic_pref})"
        )

        if song['mood'] in ['happy', 'intense']:
            danceability_score = song['danceability']
            dance_context = f"high for {song['mood']} music"
        else:
            danceability_score = 0.5
            dance_context = f"neutral for {song['mood']} music"
        danceability_contribution = weights['danceability'] * danceability_score
        score += danceability_contribution
        reasons.append(
            f"Danceability: {danceability_score:.2f} × {weights['danceability']:.2f} = +{danceability_contribution:.3f} ({dance_context})"
        )

        if target_mood == 'happy':
            valence_score = song['valence']
            valence_context = 'prefers upbeat (high valence)'
        elif target_mood in ['chill', 'relaxed']:
            valence_score = 1.0 - song['valence']
            valence_context = 'prefers mellow (low valence)'
        else:
            valence_score = 0.5
            valence_context = 'neutral valence preference'
        valence_contribution = weights['valence'] * valence_score
        score += valence_contribution
        reasons.append(
            f"Valence: {valence_score:.2f} × {weights['valence']:.2f} = +{valence_contribution:.3f} ({valence_context})"
        )

        popularity_diff = abs(song['popularity'] - target_popularity) / 100.0
        popularity_score = max(0.0, 1.0 - popularity_diff)
        popularity_contribution = weights['popularity'] * popularity_score
        score += popularity_contribution
        reasons.append(
            f"Popularity: {popularity_score:.2f} × {weights['popularity']:.2f} = +{popularity_contribution:.3f} (target={target_popularity})"
        )

        decade_score = 1.0 if preferred_decade and song['release_decade'] == preferred_decade else 0.5
        decade_contribution = weights['release_decade'] * decade_score
        score += decade_contribution
        reasons.append(
            f"Release Decade: {decade_score:.2f} × {weights['release_decade']:.2f} = +{decade_contribution:.3f} ({song['release_decade']})"
        )

        if desired_mood_tags:
            tag_matches = sum(1 for tag in desired_mood_tags if tag in song['mood_tags'])
            mood_tag_score = min(1.0, tag_matches / len(desired_mood_tags))
        else:
            tag_matches = 0
            mood_tag_score = 0.5
        mood_tag_contribution = weights['mood_tags'] * mood_tag_score
        score += mood_tag_contribution
        reasons.append(
            f"Mood Tags: {mood_tag_score:.2f} × {weights['mood_tags']:.2f} = +{mood_tag_contribution:.3f} (matched {tag_matches})"
        )

        if vocal_preference == 'instrumental':
            instrumentalness_score = song['instrumentalness']
            speechiness_score = 1.0 - song['speechiness']
            vocal_context = 'instrumental preference'
        else:
            instrumentalness_score = 1.0 - song['instrumentalness']
            speechiness_score = song['speechiness']
            vocal_context = 'vocal preference'
        instrumental_contribution = weights['instrumentalness'] * instrumentalness_score
        speechiness_contribution = weights['speechiness'] * speechiness_score
        score += instrumental_contribution + speechiness_contribution
        reasons.append(
            f"Instrumentalness: {instrumentalness_score:.2f} × {weights['instrumentalness']:.2f} = +{instrumental_contribution:.3f} ({vocal_context})"
        )
        reasons.append(
            f"Speechiness: {speechiness_score:.2f} × {weights['speechiness']:.2f} = +{speechiness_contribution:.3f} ({vocal_context})"
        )

        if listening_context:
            context_score = 1.0 if song['listening_context'] == listening_context else 0.5
            context_contribution = weights['listening_context'] * context_score
            score += context_contribution
            reasons.append(
                f"Context: {context_score:.2f} × {weights['listening_context']:.2f} = +{context_contribution:.3f} ({song['listening_context']})"
            )

        return score, reasons

    def compute_diversity_penalty(song: Dict, selected: List[Dict]) -> Tuple[float, List[str]]:
        artist_count = sum(1 for selected_song in selected if selected_song['artist'] == song['artist'])
        genre_count = sum(1 for selected_song in selected if selected_song['genre'] == song['genre'])
        penalty = artist_count * 0.08 + genre_count * 0.05
        reasons = []
        if artist_count:
            reasons.append(f"artist repeat x{artist_count}")
        if genre_count:
            reasons.append(f"genre repeat x{genre_count}")
        return penalty, reasons

    def format_explanation(song: Dict, score: float, reasons: List[str]) -> str:
        breakdown = "\n  ".join(reasons)
        return f"Score: {score:.3f}\n  {breakdown}"

    scored_songs = []
    for song in songs:
        song_score, song_reasons = score_song(song, user_prefs)
        scored_songs.append((song, song_score, song_reasons))

    selected: List[Tuple[Dict, float, List[str]]] = []
    remaining = scored_songs.copy()
    while len(selected) < k and remaining:
        best_index = None
        best_adjusted_score = -float('inf')
        best_item = None
        for idx, (song, score, reasons) in enumerate(remaining):
            penalty, penalty_reasons = compute_diversity_penalty(song, [item[0] for item in selected])
            adjusted_score = score - penalty
            if adjusted_score > best_adjusted_score:
                best_adjusted_score = adjusted_score
                best_index = idx
                best_item = (song, score, reasons, penalty, penalty_reasons)
        if best_item is None:
            break

        song, score, reasons, penalty, penalty_reasons = best_item
        chosen_reasons = list(reasons)
        final_score = score - penalty
        if penalty > 0:
            penalty_text = ", ".join(penalty_reasons)
            chosen_reasons.append(f"Diversity penalty: -{penalty:.2f} ({penalty_text})")
        selected.append((song, final_score, chosen_reasons))
        del remaining[best_index]

    recommendations = [
        (song, score, format_explanation(song, score, reasons))
        for song, score, reasons in selected
    ]

    return recommendations
