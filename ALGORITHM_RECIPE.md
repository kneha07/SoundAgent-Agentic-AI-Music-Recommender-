# 🎵 Algorithm Recipe: Music Recommender Scoring Logic

## Executive Summary

Our music recommender uses a **normalized weighted scoring system** that combines 12 audio and contextual features to produce recommendation scores from 0.0 to 1.0. This approach provides fine-grained continuous scoring that significantly outperforms simple binary point systems.

---

## The Scoring Formula

```
Score = 0.15×E + 0.12×M + 0.11×G + 0.09×A + 0.09×D + 0.07×V + 0.08×P + 0.06×R + 0.08×T + 0.06×I + 0.05×S + 0.04×C

Base Weights (sum to 1.0):
  E = Energy matching           (15%)   - Song intensity alignment
  M = Mood matching             (12%)   - Emotional/contextual intent
  G = Genre matching            (11%)   - Musical category
  A = Acousticness fit          (9%)    - Instrument type preference
  D = Danceability bonus        (9%)    - Activity context suitability
  V = Valence refinement        (7%)    - Emotional tone (upbeat vs mellow)
  P = Popularity match          (8%)    - Cultural relevance level
  R = Release decade            (6%)    - Era preference
  T = Mood tags overlap         (8%)    - Detailed mood tags
  I = Instrumentalness          (6%)    - Vocal vs instrumental
  S = Speechiness               (5%)    - Lyrics/speech content
  C = Listening context         (4%)    - Situational suitability
```

**Key Feature**: All weights sum to **1.0**, producing normalized 0.0-1.0 scores that are interpretable and comparable.

---

## Feature-by-Feature Breakdown

### 1. Energy Matching (15% base weight) — Most Important 🏋️

**Purpose**: Match song intensity to user preference

**How it works**:
```python
similarity = max(0.0, 1.0 - |song_energy - target_energy|)
```

**Example: Target energy = 0.80**
- Song @ 0.82 → 1.0 - 0.02 = **0.98** ✨ (excellent)
- Song @ 0.80 → 1.0 - 0.00 = **1.00** (perfect)
- Song @ 0.79 → 1.0 - 0.01 = **0.99** ✨ (excellent)
- Song @ 0.95 → 1.0 - 0.15 = **0.85** (acceptable but off-target)
- Song @ 0.50 → 1.0 - 0.30 = **0.70** (poor)

**Why 15%?**
- Energy is the fundamental vibe signal
- Users have clear preferences (no one mistakes workout energy for sleep music)
- Continuous scoring rewards proximity, not binary hits

---

### 2. Mood Matching (12% base weight) — Critical Context 😊

**Purpose**: Match emotional/contextual purpose of listening

**How it works**:
```python
if song.mood == target.mood:
    similarity = 1.0  # Perfect match
else:
    similarity = 0.5  # Partial credit for context diversity
```

**Categories**: happy, chill, intense, relaxed, sad, moody, focused

**Example:**
- User wants "happy" → Gets "happy" song: 1.0 ✓
- User wants "happy" → Gets "chill" song: 0.5 (useful but not ideal)
- User wants "happy" → Gets "sad" song: 0.5 (still usable)

**Why 12%?**
- Mood directly reflects user listening intent
- Weighting ensures emotional context isn't lost in numerical optimization
- Second-most impactful feature after energy

---

### 3. Genre Matching (11% base weight) — Category Preference 🎸

**Purpose**: Match musical genre preference

**How it works**:
```python
if song.genre == favorite_genre:
    similarity = 1.0  # Perfect match
else:
    similarity = 0.5  # Partial credit for genre diversity
```

**Why 11%?**
- Genre provides high-level categorization
- Important but overlaps with energy/mood signals
- Lower than mood because it's more of a category tag than a listening intent signal

---

### 4. Acousticness (9% base weight) — Instrument Preference 🎸

**Purpose**: Match acoustic (instruments) vs electronic (synth/electronic) preference

**How it works**:
```python
if user.likes_acoustic:
    similarity = song.acousticness  # Prefer high acousticness (1.0)
else:
    similarity = 1.0 - song.acousticness  # Prefer low acousticness (0.0)
```

**Range**: 0.0 (pure electronic) to 1.0 (pure acoustic)

**Examples:**
- User likes acoustic:
  - Folk song (0.95 acoustic) → 0.95 ✓
  - Synth song (0.05 acoustic) → 1.0 - 0.05 = 0.95 ✓
  
- User prefers electronic:
  - Synth song (0.05 acoustic) → 1.0 - 0.05 = 0.95 ✓
  - Folk song (0.95 acoustic) → 1.0 - 0.95 = 0.05 ✗

**Why 9%?**
- Critical differentiation: coffeeshop acoustic vibes ≠ club electronic vibes
- Separates fundamental instrument preferences

---

### 5. Danceability (9% base weight) — Activity Context 💃

**Purpose**: Match activity suitability

**How it works**:
```python
if song.mood in ['happy', 'intense']:
    similarity = song.danceability  # Party/workout songs should be danceable
else:
    similarity = 0.5  # Neutral for chill/relaxed/sad (rhythm may distract)
```

**Range**: 0.0 (not danceable) to 1.0 (very danceable)

**Examples:**
- Happy mood song with 0.88 danceability → 0.88 ✓ (parties want rhythm)
- Intense mood song with 0.66 danceability → 0.66 ✓ (workout needs movement)
- Chill mood song with 0.88 danceability → 0.50 ⚠️ (rhythm may distract)
- Sad mood song with 0.45 danceability → 0.50 ⚠️ (neutral)

**Why 9%?**
- Danceability is context-dependent, not universal
- Equal weight to acousticness due to activity-driven matching

---

### 6. Valence (7% base weight) — Emotional Tone 🎭

**Purpose**: Fine-tune emotional positivity within mood category

**Range**: 0.0 (sad/melancholic) to 1.0 (happy/upbeat)

**How it works**:
```python
if target_mood == 'happy':
    similarity = song.valence  # Higher valence = more upbeat
elif target_mood in ['chill', 'relaxed']:
    similarity = 1.0 - song.valence  # Lower valence = mellow/contemplative
else:
    similarity = 0.5  # Neutral for other moods
```

**Example:**
- User wants "happy":
  - Upbeat song (0.84 valence) → 0.84 ✓
  - Mellow happy (0.55 valence) → 0.55 ⚠️

- User wants "chill":
  - Melancholic chill (0.35 valence) → 1.0 - 0.35 = 0.65 ✓
  - Upbeat chill (0.75 valence) → 1.0 - 0.75 = 0.25 ✗

**Why 7%?**
- Refinement feature, not primary signal
- Lower weight reflects that it personalizes within mood, not across moods

---

### 7. Popularity (8% base weight) — Cultural Relevance 📈

**Purpose**: Match expected popularity level

**How it works**:
```python
similarity = max(0.0, 1.0 - |song_popularity - target_popularity| / 100.0)
```

**Example: Target popularity = 70**
- Song @ 72 → 1.0 - 0.02 = 0.98 ✓
- Song @ 40 → 1.0 - 0.30 = 0.70 (obscure)
- Song @ 95 → 1.0 - 0.25 = 0.75 (mainstream)

**Why 8%?**
- Popularity indicates cultural/commercial relevance
- Important distinction: mainstream hits vs indie/underground

---

### 8. Release Decade (6% base weight) — Era Preference 🕰️

**Purpose**: Match preferred musical era/generation

**How it works**:
```python
if song.release_decade == preferred_decade:
    similarity = 1.0  # Era match
else:
    similarity = 0.5  # Era mismatch
```

**Decades**: 1980s, 1990s, 2000s, 2010s, 2020s, etc.

**Why 6%?**
- Optional personalization, weaker than other features
- Lower weight because not all users have decade preferences

---

### 9. Mood Tags (8% base weight) — Detailed Mood Matching 🏷️

**Purpose**: Match detailed mood tags for fine-grained personalization

**How it works**:
```python
if desired_tags:
    tag_matches = sum(1 for tag in desired_tags if tag in song.mood_tags)
    similarity = min(1.0, tag_matches / len(desired_tags))
else:
    similarity = 0.5  # No tags specified
```

**Example:**
- User wants: ["energetic", "uplifting"]
- Song has: ["energetic", "uplifting", "percussive"] → 2/2 = 1.0 ✓
- Song has: ["energetic", "sad"] → 1/2 = 0.5 ⚠️
- Song has: ["slow", "melancholic"] → 0/2 = 0.0 ✗

**Why 8%?**
- Provides fine-grained control for users who specify detailed preferences
- Equal weight to other major features when tags are specified

---

### 10. Instrumentalness (6% base weight) — Vocal vs. Instrumental 🎼

**Purpose**: Match vocal preference (lyrics vs. pure music)

**How it works**:
```python
if vocal_preference == 'instrumental':
    similarity = song.instrumentalness  # Prefer instrumental (1.0 = pure music)
else:
    similarity = 1.0 - song.instrumentalness  # Prefer vocals (0.0 = pure vocals)
```

**Range**: 0.0 (purely vocal) to 1.0 (purely instrumental)

**Examples:**
- User prefers instrumental:
  - Piano solo (0.98) → 0.98 ✓
  - Vocal song (0.05) → 0.05 ✗

- User prefers vocals:
  - Vocal song (0.05) → 1.0 - 0.05 = 0.95 ✓
  - Piano solo (0.98) → 1.0 - 0.98 = 0.02 ✗

**Why 6%?**
- Important for focus scenarios (instrumental for studying)
- But less universal than energy or mood

---

### 11. Speechiness (5% base weight) — Lyrics vs. Music 🎤

**Purpose**: Match speech/lyrics content preference

**How it works**:
```python
if vocal_preference == 'vocal':
    similarity = song.speechiness  # Prefer spoken/lyrical content
else:
    similarity = 1.0 - song.speechiness  # Prefer music-heavy (less speech)
```

**Range**: 0.0 (pure music) to 1.0 (mostly speech/rap/spoken word)

**Why 5%?**
- Complements instrumentalness for fine-grained vocal control
- Lower weight because it's a refinement on vocal preference

---

### 12. Listening Context (4% base weight) — Situation Suitability 📍

**Purpose**: Match situational/contextual setting

**How it works**:
```python
if listening_context specified:
    similarity = 1.0 if song.listening_context == desired_context else 0.5
else:
    similarity not scored (context weight = 0)
```

**Contexts**: home, car, gym, party, focus, sleep, social, etc.

**Why 4%?**
- Lowest weight, situational bonus
- Not all recommendations need context matching
- Least impactful when balancing all 12 features

---

## Weight Normalization & Mode Adjustments

### Base Weights

The **default balanced weights** (above) work well for general recommendations.

### Mode-Based Adjustments

Different listening modes adjust weight distribution:

**mood-first mode** (emphasizes emotional matching):
- Increases: mood (→16%), mood_tags (→12%), valence (→11%)
- Decreases: other features to maintain normalization

**genre-first mode** (emphasizes genre):
- Increases: genre (→18%), mood (→13%), energy (→13%)
- Decreases: other features

**energy-first mode** (emphasizes intensity):
- Increases: energy (→22%), danceability (→14%)
- Decreases: lower-priority features

### Specialized Profile Adjustments

Different use cases adjust weights further:

**study**: Boosts acousticness (→16%), mood_tags (→14%), listening_context (→10%)
**party**: Boosts energy (→18%), danceability (→16%), popularity (→10%)
**workout**: Boosts energy (→20%), danceability (→14%), popularity (→10%)
**relax**: Boosts acousticness (→16%), valence (→14%), instrumentalness (→8%)

### Weight Resolution

When mode or specialized_profile overrides are applied:
1. Start with default weights
2. Merge mode overrides (only features specified are overridden)
3. Merge specialized profile overrides (only features specified are overridden)
4. Renormalize all weights to sum to exactly 1.0

**Important**: Missing features in override dicts retain their default values, then the entire weight dict is renormalized. This means the effective weight for an unspecified feature is reduced but not eliminated. Use the `resolve_weights()` helper (see below) to see effective weights for any combination.

### Debugging Weight Configurations

To understand what weights will actually be used for a given mode/profile combination, use the `resolve_weights()` helper:

```python
from src.recommender import resolve_weights

# Define overrides for a specific mode
mode_overrides = {
    'mood': 0.16,
    'mood_tags': 0.12,
    'valence': 0.11,
    # ... (other features omitted, they'll use defaults)
}

# Get final effective weights
final_weights = resolve_weights(default_weights, mode_overrides)

print("Mood-first mode effective weights:")
for feature, weight in sorted(final_weights.items()):
    print(f"  {feature}: {weight:.4f}")

# Output shows that unspecified features (energy, danceability, etc.)
# were retained and the entire dict was renormalized to 1.0
```

This helper is invaluable for understanding why certain feature combinations produce specific recommendations.

---

## Why This Approach Works

✅ **Continuous Scoring** - Rewards proximity, penalties for mismatches (not binary)  
✅ **Normalized Weights** - All scores 0.0-1.0, comparable across user profiles  
✅ **Multi-dimensional** - 12 independent features prevent false matches  
✅ **Interpretable** - Each feature score breakdown is transparent  
✅ **Extensible** - Weights easily adjusted for context/mode without changing scoring logic  
✅ **Robust** - Works gracefully when optional features (era, tags, context) are unspecified  
✅ **Proven** - Handles diverse user profiles: workout, study, party, relax  

---

## Comparison: Simple vs. Continuous Weighted Scoring

| Aspect | Simple Point System | Our 12-Feature System |
|--------|--------|-----------|
| **Feature count** | 2-3 | 12 |
| **Scoring** | Binary (0 or 1 point) | Continuous (0.0-1.0) |
| **Weight sum** | Arbitrary (4 points) | Normalized (1.0) |
| **Energy precision** | Song @ 0.82 vs 0.95 both score 1pt | 0.82→0.98, 0.95→0.85 (differentiated) |
| **Mood flexibility** | Fixed weight | Adjustable via mode/profile |
| **Context capture** | Missing | 12 dimensions of context |

**Real example**: For "I want happy, energetic, electronic":
- Simple system: Cannot differentiate between confusing matches
- Our system: Fine-grained scoring reveals true preference alignment

---

## Algorithm Implementation

**File**: [src/recommender.py](src/recommender.py)

**Key Functions**:
- OOP: `Recommender.recommend()` and `Recommender._score_song()`
- Functional: `recommend_songs()` with internal `score_song()` nested function
- Both reference the same module-level constants: `DEFAULT_WEIGHTS`, `MODE_WEIGHT_OVERRIDES`, `SPECIALIZED_PROFILE_OVERRIDES`

**Helper**: `resolve_weights(default_weights, mode_overrides, profile_overrides)` can be used to inspect effective weights for any configuration.

**Status**: ✅ Production-ready, tested, fully documented

🎵 **Ready to recommend!**
