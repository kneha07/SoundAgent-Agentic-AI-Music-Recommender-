# 🎧 Model Card: Music Recommender Simulation

## Model Name

**VibeFinder Lite**

---

## Goal / Task

This recommender tries to suggest songs that match a user’s mood, energy level, and acoustic or electronic taste. It ranks tracks from a small catalog so the most fitting songs appear first.

---

## Data Used

The system uses a catalog of 20 songs from `data/songs.csv`. Each song includes features such as genre, mood, energy, tempo, valence, danceability, and acousticness. The dataset is small and does not include every genre, mood, or listening context.

---

## Algorithm Summary

The system uses a two-stage workflow. First, an agent parses user requests into structured music preferences and retrieves candidate songs from the catalog using genre, mood, context, and tag keywords. It also pulls custom external genre notes from `data/genre_notes.csv` so recommendations are grounded in a second document source. Then the recommender scores candidates with a mode-based weighted ranking and a diversity penalty.

The system also applies specialized weight profiles for listening situations such as study, party, workout, and relax. It can detect a requested response style and adapt the recommendation tone to be company-professional, friendly, or casual. Each recommendation includes a confidence score and a validation step that can retry with a mood-first fallback when the top result does not closely match the user’s intent.

---

## Observed Behavior / Biases

The model tends to favor happy, high-energy songs because those are well represented in the dataset. It also prefers electronic tracks when the user says they like electronic sound. The system can struggle with conflicting preferences, such as a sad mood combined with very high energy.

---

## Evaluation Process

I tested four user profiles: High-Energy Pop, Chill Lofi, Deep Intense Rock, and Sad Energy Conflict. I checked the top 5 songs for each profile and compared them to the expected mood and energy. I also ran one experiment that ignored mood scoring to see how much mood was affecting the results.

---

## Intended Use and Non-Intended Use

This system is designed for learning and exploring content-based recommendation ideas. It is not meant for real music apps or production use. It should not be used to recommend music without more data, user history, or genre diversity.

---

## Ideas for Improvement

- Add more song features like genre similarity, instrumentalness, and popularity.
- Use a continuous acoustic preference instead of a simple acoustic/electronic choice.
- Add collaborative or hybrid recommendation signals.
- Increase the catalog size and balance genres and moods.

---

## Personal Reflection

The biggest learning moment was seeing that simple weighted scores can still make recommendations feel meaningful. AI helped speed up the code changes and documentation, but I had to double-check the output logic and the math in the recommender. I was surprised that a small dataset could still separate calm songs from intense ones. Next, I would try adding more features and a more varied dataset to reduce bias.
