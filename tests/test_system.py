from src.recommender import load_songs
from src.system import RecommendationAgent


def test_parse_request_extracts_preferences():
    agent = RecommendationAgent([])
    prefs = agent.parse_request('Find calm study songs for coffee with a chill mood and dreamy textures.')

    assert prefs['mood'] == 'chill'
    assert prefs['listening_context'] == 'study'
    assert prefs['acoustic_preference'] in ['acoustic', 'mixed']
    assert prefs['mode'] == 'mood-first'


def test_retrieve_relevant_songs_returns_matches():
    songs = load_songs('data/songs.csv')
    agent = RecommendationAgent(songs)
    candidates = agent.retrieve_relevant_songs('intense workout rock', limit=5)

    assert len(candidates) > 0
    assert any(song['listening_context'] == 'workout' for song in candidates)


def test_recommend_for_text_returns_confident_result():
    songs = load_songs('data/songs.csv')
    agent = RecommendationAgent(songs)
    result = agent.recommend_for_text('Recommend upbeat party music for a happy listener who loves electronic pop.', k=3)

    assert result.recommendations
    assert result.confidence >= 0.4
    assert result.mode in ['balanced', 'genre-first', 'mood-first', 'energy-first']


def test_rag_returns_retrieved_documents():
    songs = load_songs('data/songs.csv')
    agent = RecommendationAgent(songs)
    result = agent.recommend_for_text('Find chill study songs for coffee with a dreamy mood.', k=3)

    assert result.retrieved_docs
    assert len(result.retrieved_docs) > 0
    assert any('coffee' in doc['doc_text'].lower() or 'study' in doc['doc_text'].lower() for doc in result.retrieved_docs)


def test_specialized_profile_changes_recommendations():
    songs = load_songs('data/songs.csv')
    from src.recommender import recommend_songs

    prefs = {
        'mood': 'happy',
        'energy': 0.60,
        'acoustic_preference': 'mixed',
        'favorite_genre': 'pop',
        'target_popularity': 70,
        'preferred_decade': '2020s',
        'desired_mood_tags': ['bright'],
        'vocal_preference': 'vocal',
        'listening_context': 'party',
    }
    baseline = recommend_songs(prefs, songs, k=1, mode='balanced')
    specialized = recommend_songs(prefs, songs, k=1, mode='balanced', specialized_profile='party')

    assert baseline[0][0] != specialized[0][0] or baseline[0][1] != specialized[0][1]


def test_external_genre_documents_are_loaded():
    songs = load_songs('data/songs.csv')
    from src.system import RecommendationAgent

    agent = RecommendationAgent(songs)
    docs = agent.extra_documents

    assert docs
    assert any(doc.get('genre') == 'lofi' for doc in docs)
    assert any('Relaxed beats' in doc['doc_text'] or 'Relaxed beats' in doc['description'] for doc in docs)
