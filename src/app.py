import os
from typing import List, Dict

import streamlit as st

from .recommender import load_songs, recommend_songs
from .system import RecommendationAgent


def load_catalog() -> List[Dict]:
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'songs.csv')
    return load_songs(csv_path)


CUSTOM_CSS = '''
<style>
.section-title {font-size:2rem; font-weight:700; margin-bottom:0.2rem;}
.section-subtitle {color:#111827; margin-top:0; margin-bottom:1rem;}
.card {background:#ffffff; border:1px solid #cbd5e1; border-radius:18px; padding:18px; margin-bottom:18px; box-shadow:0 10px 30px rgba(15,23,42,0.08);}
.metric-box {background:#ffffff; border:1px solid #cbd5e1; border-radius:16px; padding:18px; margin-bottom:18px;}
.small-label {color:#334155; font-size:0.95rem;}
.stButton>button {background-color:#ef4444; color:#ffffff; border:none; border-radius:999px; padding:0.75rem 1.4rem; font-weight:700;}
.stButton>button:hover {background-color:#dc2626;}
.stButton>button:focus {outline:2px solid #fca5a5; outline-offset:2px;}
div[data-testid="stMarkdownContainer"] p {line-height:1.7;}
</style>
'''


def inject_page_style() -> None:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_song_card(rank: int, song: Dict, score: float) -> None:
    card_html = f'''
    <div class="card" role="group" aria-label="Song recommendation {rank}: {song['title']} by {song['artist']}">
      <div style="display:flex; justify-content:space-between; align-items:center; gap:16px; flex-wrap:wrap;">
        <div>
          <div style="font-size:1.1rem; font-weight:700; color:#0f172a;">#{rank} {song['title']}</div>
          <div style="color:#475569;">{song['artist']}</div>
        </div>
        <div style="text-align:right;">
          <div style="font-size:1rem; font-weight:700; color:#0b6efd;">{score:.3f}</div>
          <div class="small-label">Model score</div>
        </div>
      </div>
      <div style="margin-top:12px; color:#0f172a;">
        Genre: <strong>{song['genre']}</strong> • Mood: <strong>{song['mood']}</strong> • Context: <strong>{song['listening_context']}</strong>
      </div>
      <div style="margin-top:8px; color:#334155;">Tags: {', '.join(song.get('mood_tags', [])) or 'none'}</div>
    </div>
    '''
    st.markdown(card_html, unsafe_allow_html=True)


def display_recommendations(recommendations: List[tuple]) -> None:
    if not recommendations:
        st.warning('No recommendations available.')
        return

    st.subheader('Top Recommendations')
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        render_song_card(rank, song, score)

    top_song, top_score, top_explanation = recommendations[0]
    with st.expander('Why the top song was selected?', expanded=True):
        st.write(f'**{top_song["title"]}** by {top_song["artist"]} is a strong fit because it matches the requested mood, genre, and listening context.')
        st.write(top_explanation)


def build_kpi_cards(songs: List[Dict]) -> None:
    genres = len({song['genre'] for song in songs})
    contexts = len({song['listening_context'] for song in songs})
    moods = len({song['mood'] for song in songs})

    col1, col2, col3 = st.columns(3)
    col1.markdown('<div class="metric-box"><h3>🎧 Songs</h3><p style="font-size:1.8rem; font-weight:700;">{}</p></div>'.format(len(songs)), unsafe_allow_html=True)
    col2.markdown('<div class="metric-box"><h3>🎼 Genres</h3><p style="font-size:1.8rem; font-weight:700;">{}</p></div>'.format(genres), unsafe_allow_html=True)
    col3.markdown('<div class="metric-box"><h3>🧭 Contexts</h3><p style="font-size:1.8rem; font-weight:700;">{}</p></div>'.format(contexts), unsafe_allow_html=True)


def build_profile_form() -> Dict:
    with st.form(key='profile_form'):
        st.subheader('Listener Profile')
        left, right = st.columns(2)

        with left:
            mood = st.selectbox(
                'Mood',
                ['happy', 'sad', 'chill', 'relaxed', 'intense', 'focused', 'moody'],
                help='Choose the emotional tone you want the playlist to reflect.'
            )
            energy = st.slider(
                'Energy', 0.0, 1.0, 0.6, step=0.05,
                help='Higher values mean more driving, upbeat tracks; lower values mean calmer songs.'
            )
            acoustic_preference = st.selectbox(
                'Acoustic Preference',
                ['mixed', 'acoustic', 'electronic'],
                help='Select whether you prefer acoustic instruments, electronic production, or a blend.'
            )
            favorite_genre = st.selectbox(
                'Favorite Genre',
                ['none', 'pop', 'lofi', 'rock', 'house', 'synthwave', 'indie', 'ambient', 'jazz', 'metal', 'r&b', 'latin', 'blues', 'folk', 'reggae'],
                help='Pick a genre to bias recommendations toward that style.'
            )
            favorite_genre = None if favorite_genre == 'none' else favorite_genre

        with right:
            target_popularity = st.slider(
                'Target Popularity', 0, 100, 70,
                help='Use higher values for well-known hits and lower values for niche or indie tracks.'
            )
            preferred_decade = st.selectbox(
                'Preferred Decade',
                ['none', '1990s', '2000s', '2010s', '2020s'],
                help='Choose a decade if you want music with a distinct era feel.'
            )
            preferred_decade = None if preferred_decade == 'none' else preferred_decade
            desired_mood_tags = st.multiselect(
                'Desired Mood Tags',
                ['euphoric', 'bright', 'dreamy', 'aggressive', 'powerful', 'mellow', 'emotional', 'festive', 'cozy', 'warm', 'smooth', 'cosmic'],
                help='Add one or more descriptive tags to refine the emotional texture of the playlist.'
            )
            vocal_preference = st.selectbox(
                'Vocal Preference', ['vocal', 'instrumental'],
                help='Choose whether you want songs with vocals or purely instrumental tracks.'
            )

        listening_context = st.selectbox(
            'Listening Context',
            ['none', 'party', 'study', 'workout', 'relax', 'night', 'coffee', 'drive', 'beach'],
            help='Pick the setting where you expect to listen.'
        )
        listening_context = None if listening_context == 'none' else listening_context
        mode = st.selectbox(
            'Scoring Mode', ['balanced', 'mood-first', 'genre-first', 'energy-first'],
            help='Choose the ranking strategy used by the recommender.'
        )

        submit = st.form_submit_button('Recommend Profile-based Songs')

    user_prefs = {
        'mood': mood,
        'energy': energy,
        'acoustic_preference': acoustic_preference,
        'favorite_genre': favorite_genre,
        'target_popularity': target_popularity,
        'preferred_decade': preferred_decade,
        'desired_mood_tags': desired_mood_tags,
        'vocal_preference': vocal_preference,
        'listening_context': listening_context,
        'mode': mode,
    }

    return user_prefs, submit


def run_profile_app(songs: List[Dict]) -> None:
    st.header('Profile-based Recommendation Builder')
    st.write('Build a listener profile and get tailored recommendations for mood, energy, genre, and listening context.')

    left, right = st.columns([2, 1])
    with left:
        user_prefs, submitted = build_profile_form()
    with right:
        st.markdown('#### Quick tips')
        st.write('Use the profile fields to bias the recommender toward the right mood, energy level, and genre.')
        st.write('Set the target popularity to favor hits or niche discoveries.')
        st.write('Choose a listening context to make the playlist feel more appropriate for the moment.')
        st.markdown('---')
        st.markdown('#### Suggested setups')
        st.write('- Party: happy, high energy, electronic, pop')
        st.write('- Study: chill, low energy, acoustic, lofi')
        st.write('- Workout: intense, high energy, rock or pop')

    if submitted:
        recommendations = recommend_songs(user_prefs, songs, k=7, mode=user_prefs['mode'])
        st.success('Recommendations are ready! Scroll down to see the playlist.')
        display_recommendations(recommendations)
        with st.sidebar:
            st.header('Current Profile')
            st.json(user_prefs)


def run_natural_language_app(songs: List[Dict]) -> None:
    st.header('Natural Language Music Assistant')
    st.write('Describe the vibe you want and the assistant will return a personalized top playlist.')
    st.info('Tip: scroll through the sample prompts to see how natural language maps to recommendations.')

    if 'sample_request' not in st.session_state:
        st.session_state.sample_request = 'Recommend upbeat party music for a happy listener who loves electronic pop and bright energy.'

    sample_requests = [
        'Recommend upbeat party music for a happy listener who loves electronic pop and bright energy.',
        'I want calm study songs with a chill mood and dreamy textures for coffee work.',
        'Give me intense workout tracks with strong rock or pop energy and aggressive mood tags.',
        'Find sad but powerful night music that is emotional and vocal-heavy.',
    ]

    left, right = st.columns([2, 1])
    with left:
        st.write('### Sample prompts')
        sample_rows = [sample_requests[i:i+2] for i in range(0, len(sample_requests), 2)]
        for row in sample_rows:
            cols = st.columns(2)
            for idx, sample in enumerate(row):
                if cols[idx].button(sample[:25] + '...'):
                    st.session_state.sample_request = sample

        request = st.text_area(
            'Describe your ideal playlist',
            value=st.session_state.sample_request,
            height=180,
            help='Enter a natural language description of the mood, genre, and context you want.'
        )
        if st.button('Recommend from Request'):
            agent = RecommendationAgent(songs)
            result = agent.recommend_for_text(request, k=7)

            st.success('Recommendation generated — enjoy the vibe!')
            with st.expander('Parsed Preferences', expanded=True):
                st.json(result.user_prefs)
                st.write(f'**Mode:** {result.mode}')
                st.write(f'**Confidence:** {result.confidence:.2f}')
                if result.specialized_profile:
                    st.write(f'**Specialized Model:** {result.specialized_profile}')
                if result.response_tone:
                    st.write(f'**Response Tone:** {result.response_tone}')

            if result.notes:
                with st.expander('Validation Notes', expanded=False):
                    for note in result.notes:
                        st.write(f'- {note}')

            if result.retrieved_docs:
                with st.expander('Retrieved Context', expanded=False):
                    for doc in result.retrieved_docs:
                        st.write(f"**{doc['song']['title']}** by {doc['song']['artist']} ({doc['song']['genre']}, {doc['song']['mood']})")
                        st.caption(doc['doc_text'])

            display_recommendations(result.recommendations)

    with right:
        st.markdown('#### How to use this page')
        st.write('Enter a sentence describing the mood, genre, energy, and listening context you want.')
        st.write('The assistant will parse your request, retrieve matching metadata, and rank the top songs.')
        st.markdown('---')
        st.markdown('#### Best results when')
        st.write('- you mention a mood or vibe')
        st.write('- you specify a context like party, study, or workout')
        st.write('- you describe sound preferences like electronic, acoustic, or vocal')


def main() -> None:
    st.set_page_config(page_title='VibeFinder Lite', page_icon='🎵', layout='wide')
    inject_page_style()
    st.markdown('<div class="section-title">VibeFinder Lite</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">A polished interactive music recommendation assistant for moods, playlists, and listening contexts.</div>', unsafe_allow_html=True)

    songs = load_catalog()

    build_kpi_cards(songs)

    with st.sidebar:
        st.header('Quick Start')
        st.write('Choose a mode, enter your request, and get curated song recommendations in seconds.')
        st.markdown('---')
        st.write('• Use the keyboard to navigate fields and submit buttons.')
        st.write('• Clear input labels and help text improve readability for screen readers.')
        st.write('• Expand sections for detailed preferences and validation notes.')
        st.markdown('---')
        st.write(f'Catalog size: **{len(songs)} songs**')
        st.write(f'Genres: **{len({song["genre"] for song in songs})}**')

    tabs = st.tabs(['Natural language request', 'Profile builder'])
    with tabs[0]:
        run_natural_language_app(songs)
    with tabs[1]:
        run_profile_app(songs)


if __name__ == '__main__':
    main()
