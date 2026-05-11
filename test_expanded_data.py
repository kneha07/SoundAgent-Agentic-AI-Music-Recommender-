"""
Test the recommender with different user profiles using expanded dataset.
Demonstrates how the system handles diverse moods and genres.
"""

from src.recommender import load_songs, recommend_songs

def test_user_profiles():
    songs = load_songs("data/songs.csv")
    
    # Test Profile 1: Happy, Upbeat, Electronic
    print("=" * 60)
    print("PROFILE 1: Happy Workout")
    print("Preference: Happy mood, High energy (0.9), Electronic")
    print("=" * 60)
    user1 = {"mood": "happy", "energy": 0.9, "acoustic_preference": "electronic"}
    recs1 = recommend_songs(user1, songs, k=5)
    for song, score, explanation in recs1:
        print(f"{song['title']:20} | {score:.2f} | {explanation}")
    
    # Test Profile 2: Sad, Mellow, Acoustic
    print("\n" + "=" * 60)
    print("PROFILE 2: Sad, Acoustic Evening")
    print("Preference: Sad mood, Low energy (0.35), Acoustic")
    print("=" * 60)
    user2 = {"mood": "sad", "energy": 0.35, "acoustic_preference": "acoustic"}
    recs2 = recommend_songs(user2, songs, k=5)
    for song, score, explanation in recs2:
        print(f"{song['title']:20} | {score:.2f} | {explanation}")
    
    # Test Profile 3: Chill, Ambient, Late Night
    print("\n" + "=" * 60)
    print("PROFILE 3: Chill, Ambient Focus Session")
    print("Preference: Chill mood, Low energy (0.25), Acoustic")
    print("=" * 60)
    user3 = {"mood": "chill", "energy": 0.25, "acoustic_preference": "acoustic"}
    recs3 = recommend_songs(user3, songs, k=5)
    for song, score, explanation in recs3:
        print(f"{song['title']:20} | {score:.2f} | {explanation}")
    
    # Test Profile 4: Intense, Metal/Hip-Hop
    print("\n" + "=" * 60)
    print("PROFILE 4: Intense, Electronic Workout")
    print("Preference: Intense mood, High energy (0.95), Electronic")
    print("=" * 60)
    user4 = {"mood": "intense", "energy": 0.95, "acoustic_preference": "electronic"}
    recs4 = recommend_songs(user4, songs, k=5)
    for song, score, explanation in recs4:
        print(f"{song['title']:20} | {score:.2f} | {explanation}")
    
    # Test Profile 5: Relaxed, Acoustic
    print("\n" + "=" * 60)
    print("PROFILE 5: Relaxed, Acoustic Vibe")
    print("Preference: Relaxed mood, Medium energy (0.45), Acoustic")
    print("=" * 60)
    user5 = {"mood": "relaxed", "energy": 0.45, "acoustic_preference": "acoustic"}
    recs5 = recommend_songs(user5, songs, k=5)
    for song, score, explanation in recs5:
        print(f"{song['title']:20} | {score:.2f} | {explanation}")

if __name__ == "__main__":
    test_user_profiles()
