from src.recommender import Song, UserProfile, Recommender

def make_small_recommender() -> Recommender:
    songs = [
        {
            'id': 1,
            'title': "Test Pop Track",
            'artist': "Test Artist",
            'genre': "pop",
            'mood': "happy",
            'energy': 0.8,
            'tempo_bpm': 120,
            'valence': 0.9,
            'danceability': 0.8,
            'acousticness': 0.2,
            'popularity': 70,
            'release_decade': "2020s",
            'mood_tags': [],
            'instrumentalness': 0.0,
            'speechiness': 0.0,
            'listening_context': "general",
        },
        {
            'id': 2,
            'title': "Chill Lofi Loop",
            'artist': "Test Artist",
            'genre': "lofi",
            'mood': "chill",
            'energy': 0.4,
            'tempo_bpm': 80,
            'valence': 0.6,
            'danceability': 0.5,
            'acousticness': 0.9,
            'popularity': 70,
            'release_decade': "2020s",
            'mood_tags': [],
            'instrumentalness': 0.0,
            'speechiness': 0.0,
            'listening_context': "general",
        },
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user_prefs = {
        'favorite_genre': "pop",
        'mood': "happy",
        'energy': 0.8,
        'acoustic_preference': "electronic",
    }
    rec = make_small_recommender()
    results = rec.recommend(user_prefs, k=2)

    assert len(results) == 2
    # Results are now tuples: (song, score, explanation)
    songs = [song for song, _, _ in results]
    # Starter expectation: the pop, happy, high energy song should score higher
    assert songs[0]['genre'] == "pop"
    assert songs[0]['mood'] == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user_prefs = {
        'favorite_genre': "pop",
        'mood': "happy",
        'energy': 0.8,
        'acoustic_preference': "electronic",
    }
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user_prefs, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""
