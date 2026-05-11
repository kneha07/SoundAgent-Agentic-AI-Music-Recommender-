"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from .recommender import load_songs, recommend_songs
from .system import RecommendationAgent, build_sample_requests
import os


def print_recommendations(
    profile_name: str,
    user_prefs: dict,
    songs: list,
    k: int = 5,
    ignore_mood: bool = False,
    mode: str = "balanced"
) -> None:
    """Run the recommender for a profile and print a readable summary."""
    recommendations = recommend_songs(user_prefs, songs, k=k, ignore_mood=ignore_mood, mode=mode)
    print("\n" + "="*80)
    header = f"🎵 {profile_name} - Top {k} Recommendations"
    print(header)
    print("="*80)
    print(f"\n📋 User Profile:")
    print(f"   • Mood: {user_prefs['mood'].upper()}")
    print(f"   • Energy Level: {user_prefs['energy']:.1f} (0=chill, 1=intense)")
    print(f"   • Preference: {user_prefs['acoustic_preference'].upper()}")
    if user_prefs.get('favorite_genre'):
        print(f"   • Favorite Genre: {user_prefs['favorite_genre'].upper()}")
    if user_prefs.get('preferred_decade'):
        print(f"   • Era: {user_prefs['preferred_decade']}")
    print(f"   • Scoring Mode: {mode}")
    if ignore_mood:
        print("   • Experiment: mood scoring ignored")
    print("\n" + "-"*80)

    print_summary_table(recommendations)

    for i, rec in enumerate(recommendations, 1):
        song, score, explanation = rec
        print(f"\n#{i} ⭐ {song['title'].upper()}")
        print(f"   Artist: {song['artist']} | Genre: {song['genre']} | Mood: {song['mood']}")
        print(f"   Tempo: {int(song['tempo_bpm'])} BPM")
        print(f"\n   📊 FINAL SCORE: {score:.3f}/1.000 ({int(score*100)}%)")
        print(f"\n   📈 SCORING BREAKDOWN:")
        for line in explanation.split("\n"):
            if "Score:" not in line and line.strip():
                print(f"      {line.strip()}")
        print("\n" + "-"*80)


def print_summary_table(recommendations: list) -> None:
    """Print a compact ASCII summary table for the top recommendations."""
    columns = ["Rank", "Title", "Artist", "Genre", "Mood", "Score"]
    widths = [4, 24, 18, 12, 9, 7]
    row_format = " | ".join([f"{{:<{w}}}" for w in widths])
    print(row_format.format(*columns))
    print("-" * (sum(widths) + 3 * (len(widths) - 1)))
    for i, rec in enumerate(recommendations, 1):
        song, score, _ = rec
        print(
            row_format.format(
                i,
                song['title'][:widths[1]],
                song['artist'][:widths[2]],
                song['genre'][:widths[3]],
                song['mood'][:widths[4]],
                f"{score:.3f}"
            )
        )
    print()


def main() -> None:
    # Build path to songs.csv relative to project root
    csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "songs.csv")
    songs = load_songs(csv_path)

    profiles = [
        (
            "High-Energy Pop",
            {
                "mood": "happy",
                "energy": 0.90,
                "acoustic_preference": "electronic",
                "favorite_genre": "pop",
                "target_popularity": 85,
                "preferred_decade": "2020s",
                "desired_mood_tags": ["euphoric", "bright"],
                "vocal_preference": "vocal",
                "listening_context": "party"
            },
            "balanced"
        ),
        (
            "Chill Lofi",
            {
                "mood": "chill",
                "energy": 0.35,
                "acoustic_preference": "acoustic",
                "favorite_genre": "lofi",
                "target_popularity": 60,
                "preferred_decade": "2020s",
                "desired_mood_tags": ["dreamy", "mellow"],
                "vocal_preference": "instrumental",
                "listening_context": "study"
            },
            "balanced"
        ),
        (
            "Deep Intense Rock",
            {
                "mood": "intense",
                "energy": 0.95,
                "acoustic_preference": "electronic",
                "favorite_genre": "rock",
                "target_popularity": 70,
                "preferred_decade": "2010s",
                "desired_mood_tags": ["aggressive", "powerful"],
                "vocal_preference": "vocal",
                "listening_context": "workout"
            },
            "balanced"
        ),
        (
            "Sad Energy Conflict",
            {
                "mood": "sad",
                "energy": 0.90,
                "acoustic_preference": "electronic",
                "favorite_genre": "indie",
                "target_popularity": 50,
                "preferred_decade": "2010s",
                "desired_mood_tags": ["melancholy", "emotional"],
                "vocal_preference": "vocal",
                "listening_context": "night"
            },
            "balanced"
        ),
        (
            "High-Energy Pop (Genre-First)",
            {
                "mood": "happy",
                "energy": 0.90,
                "acoustic_preference": "electronic",
                "favorite_genre": "pop",
                "target_popularity": 85,
                "preferred_decade": "2020s",
                "desired_mood_tags": ["euphoric", "bright"],
                "vocal_preference": "vocal",
                "listening_context": "party"
            },
            "genre-first"
        ),
    ]

    for name, prefs, mode in profiles:
        print_recommendations(name, prefs, songs, k=5, mode=mode)

    # Experimental comparison: ignore mood scoring to see whether mood matching is driving the results.
    print_recommendations(
        "High-Energy Pop (Mood Ignored Experiment)",
        profiles[0][1],
        songs,
        k=5,
        ignore_mood=True,
        mode="balanced"
    )

    agent = RecommendationAgent(songs)
    print("\n" + "="*80)
    print("🎛️ AGENTIC RECOMMENDER TESTS")
    print("="*80)
    for request in build_sample_requests():
        result = agent.recommend_for_text(request, k=5)
        print(f"\n🔎 Request: {request}")
        print(f"Confidence: {result.confidence:.2f}")
        print(f"Mode: {result.mode}")
        for rank, (song, score, explanation) in enumerate(result.recommendations, start=1):
            print(f"  {rank}. {song['title']} ({song['genre']}, {song['mood']}) - {score:.3f}")
        if result.notes:
            print("  Notes:")
            for note in result.notes:
                print(f"    - {note}")

    print(f"\n✅ Evaluation complete! See model_card.md and reflection.md for bias and profile comparisons.\n")


if __name__ == "__main__":
    main()
