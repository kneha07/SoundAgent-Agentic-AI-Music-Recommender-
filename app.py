"""Streamlit web UI for the AI Music Recommender System."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import pandas as pd
import requests
from urllib.parse import quote_plus

from src.recommender import load_songs, recommend_songs
from src.system import RecommendationAgent

CSV_PATH = os.path.join(os.path.dirname(__file__), "data", "songs.csv")

# ── Global CSS ─────────────────────────────────────────────────────────────────
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* ── Hero Banner ─────────────────────────────────────────────────────── */
.app-hero {
    background: linear-gradient(135deg, #0a1628 0%, #0c2d48 45%, #0e3d5c 100%);
    border-radius: 20px;
    padding: 2.5rem 2.2rem;
    margin-bottom: 1.8rem;
    position: relative;
    overflow: hidden;
}
.app-hero::before {
    content: '';
    position: absolute;
    top: -40%;
    right: -5%;
    width: 380px;
    height: 380px;
    background: radial-gradient(circle, rgba(6,182,212,0.25) 0%, transparent 70%);
    pointer-events: none;
}
.app-hero h1 {
    color: #ffffff;
    font-size: 2.4rem;
    font-weight: 800;
    margin: 0 0 0.45rem 0;
    letter-spacing: -0.02em;
}
.app-hero p {
    color: #a5f3fc;
    font-size: 1.05rem;
    margin: 0;
}

/* ── Skip Navigation (accessibility) ─────────────────────────────────── */
.skip-nav {
    position: absolute;
    top: -120px;
    left: 0;
    background: #0891b2;
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 0 0 10px 0;
    text-decoration: none;
    font-weight: 600;
    z-index: 9999;
    transition: top 0.2s;
}
.skip-nav:focus { top: 0; }

/* ── KPI Cards ────────────────────────────────────────────────────────── */
.kpi-card {
    background: linear-gradient(135deg, #0a1628, #0c2d48);
    border: 1px solid rgba(6,182,212,0.3);
    border-radius: 16px;
    padding: 1.3rem 1.5rem;
    text-align: center;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.kpi-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 32px rgba(6,182,212,0.25);
}
.kpi-icon  { font-size: 1.5rem; margin-bottom: 0.4rem; }
.kpi-number { font-size: 2.1rem; font-weight: 800; color: #22d3ee; line-height: 1; }
.kpi-label  { color: #a5f3fc; font-size: 0.85rem; font-weight: 500; margin-top: 0.35rem; }

/* ── Section Headers ──────────────────────────────────────────────────── */
.section-header {
    display: flex;
    align-items: center;
    gap: 0.65rem;
    margin-bottom: 1.4rem;
    padding-bottom: 0.65rem;
    border-bottom: 2px solid rgba(6,182,212,0.18);
}
.section-header h2 { font-size: 1.3rem; font-weight: 700; color: #0c2d48; margin: 0; }
.section-badge {
    background: linear-gradient(135deg, #0891b2, #06b6d4);
    color: white;
    font-size: 0.72rem;
    font-weight: 600;
    padding: 0.18rem 0.65rem;
    border-radius: 99px;
    letter-spacing: 0.02em;
}

/* ── Buttons ──────────────────────────────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, #0891b2, #06b6d4) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.6rem 1.5rem !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
    letter-spacing: 0.01em !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 14px rgba(8,145,178,0.35) !important;
    cursor: pointer !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #0e7490, #0891b2) !important;
    box-shadow: 0 6px 22px rgba(8,145,178,0.5) !important;
    transform: translateY(-1px) !important;
}
.stButton > button:focus-visible {
    outline: 3px solid #22d3ee !important;
    outline-offset: 3px !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
    box-shadow: 0 2px 8px rgba(8,145,178,0.3) !important;
}

/* ── Tab Bar ──────────────────────────────────────────────────────────── */
div[data-testid="stTabs"] button[role="tab"] {
    font-weight: 600 !important;
    font-size: 0.92rem !important;
    padding: 0.55rem 1.3rem !important;
    border-radius: 10px 10px 0 0 !important;
    color: #6b7280 !important;
    transition: all 0.2s !important;
}
div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    color: #0891b2 !important;
    border-bottom: 3px solid #0891b2 !important;
    background: rgba(8,145,178,0.05) !important;
}
div[data-testid="stTabs"] button[role="tab"]:hover {
    color: #0891b2 !important;
    background: rgba(8,145,178,0.05) !important;
}
div[data-testid="stTabs"] button[role="tab"]:focus-visible {
    outline: 2px solid #22d3ee !important;
    outline-offset: 2px !important;
}

/* ── Form Controls ────────────────────────────────────────────────────── */
div[data-testid="stSelectbox"] > div > div,
div[data-testid="stMultiSelect"] > div > div {
    border-radius: 10px !important;
    border-color: #a5f3fc !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
div[data-testid="stSelectbox"] > div > div:focus-within,
div[data-testid="stMultiSelect"] > div > div:focus-within {
    border-color: #0891b2 !important;
    box-shadow: 0 0 0 3px rgba(8,145,178,0.15) !important;
}

/* Slider accent */
div[data-testid="stSlider"] div[role="slider"] { background: #0891b2 !important; }

/* Toggle */
div[data-testid="stToggle"] span[data-checked="true"] { background: #0891b2 !important; }
div[data-testid="stToggle"] label { font-weight: 500 !important; color: #374151 !important; }

/* Text inputs */
textarea, input[type="text"] {
    border-radius: 10px !important;
    border: 1.5px solid #a5f3fc !important;
    font-family: inherit !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
textarea:focus, input[type="text"]:focus {
    border-color: #0891b2 !important;
    box-shadow: 0 0 0 3px rgba(8,145,178,0.15) !important;
    outline: none !important;
}

/* ── DataFrames / Tables ──────────────────────────────────────────────── */
div[data-testid="stDataFrame"] {
    border-radius: 14px !important;
    overflow: hidden !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.07) !important;
    border: 1px solid #cffafe !important;
}

/* ── Expanders ────────────────────────────────────────────────────────── */
div[data-testid="stExpander"] {
    border: 1px solid #cffafe !important;
    border-radius: 12px !important;
    overflow: hidden !important;
    margin-bottom: 0.7rem !important;
}
div[data-testid="stExpander"] > div:first-child {
    background: rgba(6,182,212,0.04) !important;
}

/* ── Song Cards ───────────────────────────────────────────────────────── */
.song-card {
    background: #ffffff;
    border: 1px solid #cffafe;
    border-left: 4px solid #0891b2;
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 0.9rem;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
    position: relative;
}
.song-card:hover {
    transform: translateX(4px);
    box-shadow: 0 6px 24px rgba(8,145,178,0.12);
}
.song-rank {
    position: absolute;
    top: -0.5rem;
    left: 1rem;
    background: linear-gradient(135deg, #0891b2, #06b6d4);
    color: white;
    font-size: 0.72rem;
    font-weight: 700;
    padding: 0.14rem 0.5rem;
    border-radius: 99px;
}
.song-title  { font-size: 1.02rem; font-weight: 700; color: #0c2d48; margin: 0.2rem 0 0.1rem; }
.song-artist { color: #6b7280; font-size: 0.88rem; }
.score-bar-track {
    background: #ecfeff;
    border-radius: 99px;
    height: 7px;
    overflow: hidden;
    margin-top: 0.65rem;
}
.score-bar-fill {
    background: linear-gradient(90deg, #0891b2, #06b6d4);
    height: 100%;
    border-radius: 99px;
}
.score-label { font-size: 0.78rem; color: #0891b2; font-weight: 600; margin-top: 0.18rem; }

/* Tag pills */
.tag-pill {
    display: inline-block;
    background: rgba(6,182,212,0.09);
    color: #0e7490;
    border: 1px solid rgba(6,182,212,0.25);
    border-radius: 99px;
    font-size: 0.73rem;
    font-weight: 500;
    padding: 0.12rem 0.52rem;
    margin: 0.12rem 0.12rem 0 0;
}
.tag-pill.genre   { background: rgba(16,185,129,0.08);  color: #065f46; border-color: rgba(16,185,129,0.2); }
.tag-pill.mood    { background: rgba(245,158,11,0.09);  color: #92400e; border-color: rgba(245,158,11,0.2); }
.tag-pill.context { background: rgba(59,130,246,0.08);  color: #1e40af; border-color: rgba(59,130,246,0.2); }

/* ── Metric ───────────────────────────────────────────────────────────── */
div[data-testid="stMetric"] {
    background: #ecfeff;
    border: 1px solid #cffafe;
    border-radius: 12px;
    padding: 0.7rem 1rem;
}
div[data-testid="stMetric"] label { color: #0891b2 !important; font-weight: 600 !important; }

/* ── Sidebar ──────────────────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a1628 0%, #0c2d48 100%) !important;
}
section[data-testid="stSidebar"] * { color: #cffafe !important; }
section[data-testid="stSidebar"] hr { border-color: rgba(6,182,212,0.3) !important; }

/* ── Misc Helpers ─────────────────────────────────────────────────────── */
.help-tip {
    background: #ecfeff;
    border-left: 3px solid #0891b2;
    border-radius: 0 10px 10px 0;
    padding: 0.75rem 1rem;
    font-size: 0.87rem;
    color: #0e4f5c;
    margin-bottom: 0.75rem;
    line-height: 1.5;
}
.setup-card {
    background: #f0fdff;
    border: 1px solid #cffafe;
    border-radius: 12px;
    padding: 0.9rem 1rem;
    margin-bottom: 0.5rem;
    transition: box-shadow 0.15s;
}
.setup-card:hover { box-shadow: 0 4px 14px rgba(8,145,178,0.1); }
.setup-card .name { color: #0e7490; font-size: 0.88rem; font-weight: 700; display: block; margin-bottom: 0.25rem; }
.setup-card .desc { color: #4b5563; font-size: 0.8rem; }

.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 300px;
    gap: 0.85rem;
    border: 2px dashed #a5f3fc;
    border-radius: 16px;
    padding: 2rem;
    margin-bottom: 1.5rem;
}

.stSpinner > div { border-top-color: #0891b2 !important; }
hr { border: none !important; border-top: 1px solid #cffafe !important; }
div[data-testid="stAlert"] { border-radius: 12px !important; border: none !important; }
</style>
"""


# ── Data ───────────────────────────────────────────────────────────────────────
@st.cache_data
def get_songs():
    return load_songs(CSV_PATH)


@st.cache_data(show_spinner=False)
def get_itunes_preview(title: str, artist: str) -> str | None:
    try:
        q = quote_plus(f"{title} {artist}")
        r = requests.get(
            f"https://itunes.apple.com/search?term={q}&entity=song&limit=1",
            timeout=4,
        )
        results = r.json().get("results", [])
        return results[0].get("previewUrl") if results else None
    except Exception:
        return None


# ── UI Components ──────────────────────────────────────────────────────────────
def render_hero():
    st.markdown("""
    <div class="app-hero" role="banner">
      <a href="#main-content" class="skip-nav">Skip to main content</a>
      <h1>🎵 VibeFinder</h1>
      <p>AI-powered music recommendations tailored to your mood, energy, and listening context</p>
    </div>
    """, unsafe_allow_html=True)


def render_kpi_row(songs):
    genres   = len({s["genre"]             for s in songs})
    moods    = len({s["mood"]              for s in songs})
    contexts = len({s["listening_context"] for s in songs})

    c1, c2, c3, c4 = st.columns(4)
    for col, icon, val, label in [
        (c1, "🎵", len(songs), "Songs in catalog"),
        (c2, "🎼", genres,     "Genres available"),
        (c3, "🌈", moods,      "Mood categories"),
        (c4, "📍", contexts,   "Listening contexts"),
    ]:
        col.markdown(
            f'<div class="kpi-card" role="img" aria-label="{val} {label}">'
            f'<div class="kpi-icon">{icon}</div>'
            f'<div class="kpi-number">{val}</div>'
            f'<div class="kpi-label">{label}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )


def render_song_card(rank: int, song: dict, score: float):
    pct  = int(score * 100)
    tags = (
        f'<span class="tag-pill genre">{song["genre"]}</span>'
        f'<span class="tag-pill mood">{song["mood"]}</span>'
        + (f'<span class="tag-pill context">{song["listening_context"]}</span>'
           if song.get("listening_context") else "")
        + "".join(
            f'<span class="tag-pill">{t}</span>'
            for t in (song.get("mood_tags") or [])[:3]
        )
    )
    query      = quote_plus(f'{song["title"]} {song["artist"]}')
    yt_url     = f"https://www.youtube.com/results?search_query={query}"
    spot_url   = f"https://open.spotify.com/search/{query}"
    play_links = (
        f'<div style="margin-top:0.7rem;display:flex;gap:0.5rem;flex-wrap:wrap;">'
        f'  <a href="{yt_url}" target="_blank" rel="noopener" style="display:inline-flex;align-items:center;gap:0.3rem;'
        f'     background:#ff0000;color:#fff;text-decoration:none;font-size:0.76rem;font-weight:600;'
        f'     padding:0.22rem 0.7rem;border-radius:99px;">▶ YouTube</a>'
        f'  <a href="{spot_url}" target="_blank" rel="noopener" style="display:inline-flex;align-items:center;gap:0.3rem;'
        f'     background:#1db954;color:#fff;text-decoration:none;font-size:0.76rem;font-weight:600;'
        f'     padding:0.22rem 0.7rem;border-radius:99px;">🎵 Spotify</a>'
        f'</div>'
    )
    st.markdown(
        f'<article class="song-card" aria-label="Rank {rank}: {song["title"]} by {song["artist"]}">'
        f'  <span class="song-rank" aria-hidden="true">#{rank}</span>'
        f'  <div class="song-title">{song["title"]}</div>'
        f'  <div class="song-artist">{song["artist"]}</div>'
        f'  <div style="margin-top:0.45rem">{tags}</div>'
        f'  <div aria-label="Match score {pct} percent">'
        f'    <div class="score-bar-track">'
        f'      <div class="score-bar-fill" style="width:{pct}%"></div>'
        f'    </div>'
        f'    <div class="score-label">{score:.3f} match score</div>'
        f'  </div>'
        f'  {play_links}'
        f'</article>',
        unsafe_allow_html=True,
    )
    preview_url = get_itunes_preview(song["title"], song["artist"])
    if preview_url:
        st.audio(preview_url, format="audio/mp4")


def render_results_table(results):
    rows = []
    for i, (song, score, _) in enumerate(results, 1):
        rows.append({
            "Rank":    i,
            "Title":   song["title"],
            "Artist":  song["artist"],
            "Genre":   song["genre"],
            "Mood":    song["mood"],
            "BPM":     int(song["tempo_bpm"]),
            "Score":   f"{score:.3f}",
            "Match":   f"{int(score * 100)}%",
        })
    st.dataframe(
        pd.DataFrame(rows),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Rank":  st.column_config.NumberColumn(width="small"),
            "BPM":   st.column_config.NumberColumn(width="small"),
            "Score": st.column_config.TextColumn(width="small"),
            "Match": st.column_config.TextColumn(width="small"),
        },
    )


def view_switcher(key: str):
    return st.radio(
        "View as",
        ["🃏 Cards", "📋 Table"],
        horizontal=True,
        key=key,
        label_visibility="visible",
    )


# ── Tab 1: Profile Builder ─────────────────────────────────────────────────────
def run_profile_tab(songs):
    st.markdown('<div id="main-content"></div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2], gap="large")

    with col1:
        st.markdown("""
        <div class="section-header">
          <span>🎛️</span><h2>Your Preferences</h2>
          <span class="section-badge">Profile Builder</span>
        </div>""", unsafe_allow_html=True)

        mood = st.selectbox("Mood",
            ["happy", "chill", "sad", "intense", "relaxed", "focused", "moody"],
            help="Emotional tone for your playlist.")
        energy = st.slider("Energy Level", 0.0, 1.0, 0.7, 0.05,
            help="0 = ultra-chill  ·  1 = high-intensity")
        acoustic_pref = st.selectbox("Sound Preference",
            ["electronic", "acoustic", "mixed"],
            help="Electronic production, acoustic instruments, or both.")
        favorite_genre = st.selectbox("Favorite Genre",
            ["pop", "lofi", "rock", "house", "indie", "metal", "r&b",
             "latin", "jazz", "synthwave", "ambient", "blues", "folk", "reggae", "hip-hop"])
        target_popularity = st.slider("Target Popularity", 0, 100, 70, 5,
            help="Higher = mainstream  ·  Lower = niche discoveries")
        preferred_decade = st.selectbox("Preferred Era",
            ["2020s", "2010s", "2000s", "1990s"])
        vocal_pref = st.selectbox("Vocal Preference", ["vocal", "instrumental"],
            help="Songs with vocals or purely instrumental.")
        context = st.selectbox("Listening Context",
            ["party", "study", "workout", "relax", "night", "coffee", "drive", "beach"])
        mood_tags_input = st.text_input("Desired Mood Tags",
            placeholder="e.g. euphoric, bright, dreamy",
            help="Comma-separated tags to fine-tune the emotional texture.")
        mode = st.selectbox("Scoring Mode",
            ["balanced", "genre-first", "mood-first", "energy-first"],
            help="Ranking strategy used by the recommender.")

        st.divider()

        ignore_mood = st.toggle("Ignore mood in scoring",
            help="Experiment: see how results change when mood matching is disabled.")
        k = st.slider("Number of recommendations", 3, 10, 5)

        run = st.button("🎵  Get Recommendations", type="primary", use_container_width=True)

    with col2:
        if run:
            desired_tags = [t.strip() for t in mood_tags_input.split(",") if t.strip()]
            prefs = {
                "mood":               mood,
                "energy":             energy,
                "acoustic_preference": acoustic_pref,
                "favorite_genre":     favorite_genre,
                "target_popularity":  target_popularity,
                "preferred_decade":   preferred_decade,
                "vocal_preference":   vocal_pref,
                "listening_context":  context,
                "desired_mood_tags":  desired_tags,
            }

            with st.spinner("Finding your perfect tracks…"):
                results = recommend_songs(prefs, songs, k=k, ignore_mood=ignore_mood, mode=mode)

            st.success(f"Found {len(results)} recommendations for your **{mood}** vibe!")

            st.markdown(
                f'<div class="section-header"><span>🎶</span>'
                f'<h2>Top {k} Picks</h2></div>',
                unsafe_allow_html=True,
            )

            choice = view_switcher("profile_view")

            if "Cards" in choice:
                for i, (song, score, _) in enumerate(results, 1):
                    render_song_card(i, song, score)
            else:
                render_results_table(results)

            st.divider()

            with st.expander("Why these songs? — Top pick breakdown"):
                top_song, _, top_explanation = results[0]
                lines = [l.strip() for l in top_explanation.split("\n")
                         if l.strip() and "Score:" not in l]
                st.markdown(f"**{top_song['title']}** by {top_song['artist']}")
                st.code("\n".join(lines), language=None)

            with st.sidebar:
                st.markdown("### 📋 Active Profile")
                st.json(prefs)

        else:
            st.markdown("""
            <div class="empty-state">
              <span style="font-size:3rem">🎵</span>
              <p style="color:#0891b2;font-weight:600;margin:0;text-align:center;">
                Set your preferences and click <strong>Get Recommendations</strong>
              </p>
              <p style="color:#9ca3af;font-size:0.84rem;margin:0;text-align:center;">
                Your personalized playlist will appear here
              </p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("**Quick setup ideas**")
            setups = [
                ("🎉 Party",     "happy · high energy · electronic · pop"),
                ("📚 Study",     "chill · low energy · acoustic · lofi"),
                ("💪 Workout",   "intense · high energy · rock or pop"),
                ("🌙 Wind Down", "relaxed · low energy · ambient · night"),
            ]
            r1, r2 = st.columns(2)
            for i, (name, desc) in enumerate(setups):
                with (r1 if i % 2 == 0 else r2):
                    st.markdown(
                        f'<div class="setup-card">'
                        f'<span class="name">{name}</span>'
                        f'<span class="desc">{desc}</span>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )


# ── Tab 2: Natural Language ────────────────────────────────────────────────────
def run_nl_tab(songs):
    left, right = st.columns([2, 1], gap="large")

    with left:
        st.markdown("""
        <div class="section-header">
          <span>💬</span><h2>Natural Language Request</h2>
          <span class="section-badge">AI-Powered</span>
        </div>""", unsafe_allow_html=True)

        examples = [
            "Upbeat party music for a happy listener who loves electronic pop and bright energy.",
            "Calm study songs with a chill mood and dreamy textures for coffee work.",
            "Intense workout tracks with strong rock or pop energy and aggressive mood tags.",
            "Sad but powerful night music that is emotional and vocal-heavy.",
        ]

        st.markdown("**Try a sample prompt:**")
        ex_c1, ex_c2 = st.columns(2)
        for i, ex in enumerate(examples):
            btn_col = ex_c1 if i % 2 == 0 else ex_c2
            if btn_col.button(ex[:44] + "…", key=f"ex_{i}", help=ex, use_container_width=True):
                st.session_state["nl_request"] = ex

        st.divider()

        request_text = st.text_area(
            "Describe your ideal playlist",
            value=st.session_state.get("nl_request", ""),
            height=95,
            placeholder="e.g. Give me energetic pop music for a morning run with bright, euphoric vibes…",
            help="Describe the mood, genre, energy, and context you want.",
        )
        k2 = st.slider("Number of results", 3, 10, 5, key="k2")

        find = st.button("🔍  Find My Songs", type="primary", use_container_width=True)

        if find:
            if not request_text.strip():
                st.warning("Please describe what you want to hear.")
            else:
                with st.spinner("Claude is parsing your request and finding matches…"):
                    agent  = RecommendationAgent(songs)
                    result = agent.recommend_for_text(request_text, k=k2)

                st.success(
                    f"Mode: **{result.mode}** · Confidence: **{result.confidence:.0%}**"
                )

                st.markdown(
                    '<div class="section-header"><span>🎶</span><h2>Your Playlist</h2></div>',
                    unsafe_allow_html=True,
                )

                choice = view_switcher("nl_view")

                if "Cards" in choice:
                    for i, (song, score, _) in enumerate(result.recommendations, 1):
                        render_song_card(i, song, score)
                else:
                    render_results_table(result.recommendations)

                if result.ai_explanation:
                    with st.expander("🤖 Why these songs? (AI Explanation)", expanded=True):
                        st.markdown(result.ai_explanation)

                if result.notes:
                    with st.expander("Validation notes"):
                        for note in result.notes:
                            st.markdown(f"- {note}")

                with st.expander("Parsed preferences"):
                    c1, c2 = st.columns(2)
                    c1.metric("Mode",       result.mode)
                    c2.metric("Confidence", f"{result.confidence:.0%}")
                    st.json(result.user_prefs)

    with right:
        st.markdown("""
        <div class="help-tip" role="note">
          <strong>How it works</strong><br>
          Describe the vibe in plain English. The AI parses your words and
          finds the best-matching songs from the catalog.
        </div>""", unsafe_allow_html=True)

        st.markdown("**For best results, mention:**")
        tips = [
            ("🎭", "A mood",        "happy, chill, intense…"),
            ("📍", "A context",     "party, study, workout…"),
            ("🎸", "Sound type",    "acoustic, electronic…"),
            ("⚡", "Energy level",  "upbeat, calm, driving…"),
        ]
        for icon, label, example in tips:
            st.markdown(
                f'<div style="display:flex;gap:0.55rem;align-items:flex-start;margin-bottom:0.6rem">'
                f'  <span style="font-size:1.05rem">{icon}</span>'
                f'  <div>'
                f'    <div style="font-weight:600;font-size:0.86rem;color:#0c2d48">{label}</div>'
                f'    <div style="font-size:0.79rem;color:#6b7280">{example}</div>'
                f'  </div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        st.markdown("---")
        st.markdown("""
        <div class="help-tip">
          <strong>Accessibility</strong><br>
          All controls support full keyboard navigation and screen readers.
          Focus rings are visible on every interactive element.
        </div>""", unsafe_allow_html=True)


# ── Tab 3: Playlists ───────────────────────────────────────────────────────────
PLAYLISTS = [
    {
        "name": "🎉 Party Starter",
        "description": "High-energy bangers to get the crowd moving.",
        "prefs": {
            "mood": "happy", "energy": 0.9, "acoustic_preference": "electronic",
            "favorite_genre": "pop", "target_popularity": 80, "preferred_decade": "2020s",
            "vocal_preference": "vocal", "listening_context": "party",
            "desired_mood_tags": ["euphoric", "bright"],
        },
        "mode": "genre-first",
    },
    {
        "name": "📚 Deep Focus",
        "description": "Calm, instrumental-friendly tracks for studying or focused work.",
        "prefs": {
            "mood": "chill", "energy": 0.3, "acoustic_preference": "acoustic",
            "favorite_genre": "lofi", "target_popularity": 55, "preferred_decade": "2020s",
            "vocal_preference": "instrumental", "listening_context": "study",
            "desired_mood_tags": ["dreamy", "focused"],
        },
        "mode": "mood-first",
    },
    {
        "name": "💪 Pump Up",
        "description": "Intense, driving tracks to push your workout harder.",
        "prefs": {
            "mood": "intense", "energy": 0.95, "acoustic_preference": "electronic",
            "favorite_genre": "rock", "target_popularity": 72, "preferred_decade": "2010s",
            "vocal_preference": "vocal", "listening_context": "workout",
            "desired_mood_tags": ["aggressive", "powerful"],
        },
        "mode": "energy-first",
    },
    {
        "name": "🌙 Night Vibes",
        "description": "Moody, atmospheric songs for late nights.",
        "prefs": {
            "mood": "moody", "energy": 0.45, "acoustic_preference": "mixed",
            "favorite_genre": "ambient", "target_popularity": 60, "preferred_decade": "2020s",
            "vocal_preference": "vocal", "listening_context": "night",
            "desired_mood_tags": ["dark", "emotional"],
        },
        "mode": "mood-first",
    },
    {
        "name": "☀️ Morning Energy",
        "description": "Bright, uplifting tracks to start your day right.",
        "prefs": {
            "mood": "happy", "energy": 0.72, "acoustic_preference": "mixed",
            "favorite_genre": "pop", "target_popularity": 78, "preferred_decade": "2020s",
            "vocal_preference": "vocal", "listening_context": "drive",
            "desired_mood_tags": ["bright", "uplifting"],
        },
        "mode": "balanced",
    },
    {
        "name": "☕ Coffee Shop",
        "description": "Easy-going acoustic vibes for a relaxed afternoon.",
        "prefs": {
            "mood": "relaxed", "energy": 0.38, "acoustic_preference": "acoustic",
            "favorite_genre": "indie", "target_popularity": 62, "preferred_decade": "2020s",
            "vocal_preference": "vocal", "listening_context": "coffee",
            "desired_mood_tags": ["mellow", "warm"],
        },
        "mode": "mood-first",
    },
]


def run_playlists_tab(songs):
    st.markdown("""
    <div class="section-header">
      <span>🎧</span><h2>Ready-Made Playlists</h2>
      <span class="section-badge">Curated</span>
    </div>""", unsafe_allow_html=True)

    cols = st.columns(3)
    selected = st.session_state.get("selected_playlist")

    for i, pl in enumerate(PLAYLISTS):
        with cols[i % 3]:
            active = selected == i
            border = "#0891b2" if active else "rgba(6,182,212,0.3)"
            bg = "rgba(8,145,178,0.07)" if active else "#ffffff"
            st.markdown(
                f'<div style="background:{bg};border:2px solid {border};border-radius:16px;'
                f'padding:1.2rem 1.3rem;margin-bottom:0.5rem;min-height:90px;">'
                f'<div style="font-size:1.08rem;font-weight:700;color:#0c2d48;margin-bottom:0.3rem">{pl["name"]}</div>'
                f'<div style="font-size:0.82rem;color:#6b7280">{pl["description"]}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            if st.button("Play", key=f"pl_{i}", use_container_width=True):
                st.session_state["selected_playlist"] = i
                st.rerun()

    if selected is not None:
        pl = PLAYLISTS[selected]
        st.divider()
        st.markdown(
            f'<div class="section-header"><span>🎶</span><h2>{pl["name"]}</h2></div>',
            unsafe_allow_html=True,
        )

        with st.spinner("Building playlist…"):
            results = recommend_songs(pl["prefs"], songs, k=6, mode=pl["mode"])

        choice = view_switcher("pl_view")
        if "Cards" in choice:
            for i, (song, score, _) in enumerate(results, 1):
                render_song_card(i, song, score)
        else:
            render_results_table(results)

        with st.expander("Playlist settings"):
            st.json(pl["prefs"])


# ── Entry Point ────────────────────────────────────────────────────────────────
def main():
    st.set_page_config(
        page_title="VibeFinder — AI Music Recommender",
        page_icon="🎵",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    songs = get_songs()

    render_hero()
    render_kpi_row(songs)
    st.markdown("<br>", unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("## 🎵 VibeFinder")
        st.markdown("---")
        st.markdown(f"**{len(songs)}** songs in catalog")
        st.markdown(f"**{len({s['genre'] for s in songs})}** genres")
        st.markdown(f"**{len({s['mood']  for s in songs})}** moods")
        st.markdown("---")
        st.markdown("**Accessibility**")
        st.markdown("- Full keyboard navigation")
        st.markdown("- Screen-reader labels")
        st.markdown("- High-contrast colors")
        st.markdown("- WCAG AA compliant")

    tab1, tab2, tab3 = st.tabs(["🎛️  Profile Builder", "💬  Natural Language", "🎧  Playlists"])
    with tab1:
        run_profile_tab(songs)
    with tab2:
        run_nl_tab(songs)
    with tab3:
        run_playlists_tab(songs)


if __name__ == "__main__":
    main()
