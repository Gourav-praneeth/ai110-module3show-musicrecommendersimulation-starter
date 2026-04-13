from typing import List, Dict, Tuple, Optional
import csv
from dataclasses import dataclass, field


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
    # Challenge 1: Advanced song features
    popularity: float = 0.0           # 0-100 popularity score
    release_decade: str = "2020s"     # e.g., "1990s", "2000s", "2010s", "2020s"
    mood_tags: List[str] = field(default_factory=list)  # detailed tags, e.g., ["nostalgic", "euphoric"]
    instrumental: bool = False
    explicit: bool = False


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
    # Challenge 1: Extended preferences for new song features
    preferred_decade: str = ""                                    # e.g., "1990s", "" = no preference
    prefer_instrumental: bool = False
    preferred_mood_tags: List[str] = field(default_factory=list)  # e.g., ["nostalgic", "euphoric"]
    min_popularity: float = 0.0                                   # minimum popularity threshold (0-100)


# ---------------------------------------------------------------------------
# Challenge 2: Scoring Mode Strategies (Strategy Pattern)
# Each mode defines a different weight profile for ranking signals.
# Switch modes in main.py by passing mode="genre_first" etc.
# ---------------------------------------------------------------------------
SCORING_MODES: Dict[str, Dict[str, float]] = {
    "default": {
        "genre": 3.0,
        "mood": 2.0,
        "energy_scale": 1.5,
        "acoustic": 1.0,
        "popularity": 0.5,
        "decade": 1.0,
        "mood_tags": 1.5,
    },
    # Genre-First: genre is the dominant ranking signal
    "genre_first": {
        "genre": 5.0,
        "mood": 1.5,
        "energy_scale": 1.0,
        "acoustic": 0.5,
        "popularity": 0.5,
        "decade": 1.0,
        "mood_tags": 1.0,
    },
    # Mood-First: mood + mood_tags drive the ranking
    "mood_first": {
        "genre": 1.5,
        "mood": 5.0,
        "energy_scale": 1.5,
        "acoustic": 0.5,
        "popularity": 0.5,
        "decade": 1.0,
        "mood_tags": 2.5,
    },
    # Energy-Focused: tracks closest in energy float to the top
    "energy_focused": {
        "genre": 1.0,
        "mood": 1.0,
        "energy_scale": 4.0,
        "acoustic": 0.5,
        "popularity": 1.0,
        "decade": 0.5,
        "mood_tags": 0.5,
    },
}


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5, weights: Optional[Dict] = None) -> List[Song]:
        scored = [(song, self._score(user, song, weights)) for song in self.songs]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [song for song, _ in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        reasons = []
        if song.genre == user.favorite_genre:
            reasons.append(f"genre matches ({song.genre})")
        if song.mood == user.favorite_mood:
            reasons.append(f"mood matches ({song.mood})")
        energy_diff = abs(song.energy - user.target_energy)
        if energy_diff <= 0.2:
            reasons.append(f"energy is close to your preference ({song.energy:.2f})")
        if user.likes_acoustic and song.acousticness >= 0.6:
            reasons.append(f"has high acousticness ({song.acousticness:.2f})")
        # Challenge 1: Explain new features
        if user.preferred_decade and song.release_decade == user.preferred_decade:
            reasons.append(f"from preferred era ({song.release_decade})")
        if user.preferred_mood_tags and song.mood_tags:
            matched = [tag for tag in user.preferred_mood_tags if tag in song.mood_tags]
            if matched:
                reasons.append(f"mood tags: {', '.join(matched)}")
        if user.prefer_instrumental and song.instrumental:
            reasons.append("instrumental track")
        if song.popularity >= 75:
            reasons.append(f"popular ({song.popularity:.0f}/100)")
        if reasons:
            return "Recommended because: " + ", ".join(reasons)
        return "Closest overall match based on genre, mood, and energy"

    def _score(self, user: UserProfile, song: Song, weights: Optional[Dict] = None) -> float:
        w = weights or SCORING_MODES["default"]
        w_genre    = w.get("genre", 3.0)
        w_mood     = w.get("mood", 2.0)
        w_energy   = w.get("energy_scale", 1.5)
        w_acoustic = w.get("acoustic", 1.0)
        w_pop      = w.get("popularity", 0.5)
        w_decade   = w.get("decade", 1.0)
        w_tags     = w.get("mood_tags", 1.5)

        score = 0.0
        if song.genre == user.favorite_genre:
            score += w_genre
        if song.mood == user.favorite_mood:
            score += w_mood
        score += (1 - abs(song.energy - user.target_energy)) * w_energy
        if user.likes_acoustic:
            score += song.acousticness * w_acoustic

        # Challenge 1: Score on new song features
        score += (song.popularity / 100.0) * w_pop
        if user.preferred_decade and song.release_decade == user.preferred_decade:
            score += w_decade
        if user.preferred_mood_tags and song.mood_tags:
            matched = [t for t in user.preferred_mood_tags if t in song.mood_tags]
            if matched:
                score += (len(matched) / len(user.preferred_mood_tags)) * w_tags
        if user.prefer_instrumental and song.instrumental:
            score += 0.5

        return score


# ---------------------------------------------------------------------------
# Functional helpers
# ---------------------------------------------------------------------------

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    songs = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["energy"]       = float(row["energy"])
            row["tempo_bpm"]    = float(row["tempo_bpm"])
            row["valence"]      = float(row["valence"])
            row["danceability"] = float(row["danceability"])
            row["acousticness"] = float(row["acousticness"])
            # Challenge 1: Parse new columns
            if "popularity" in row:
                row["popularity"] = float(row["popularity"])
            if "mood_tags" in row:
                row["mood_tags"] = [t.strip() for t in row["mood_tags"].split("|") if t.strip()]
            if "instrumental" in row:
                row["instrumental"] = row["instrumental"].strip().lower() == "true"
            if "explicit" in row:
                row["explicit"] = row["explicit"].strip().lower() == "true"
            songs.append(row)
    print(f"Loaded {len(songs)} songs from {csv_path}")
    return songs


def _score_base_signals(
    user_prefs: Dict,
    song: Dict,
    w_genre: float,
    w_mood: float,
    w_energy: float,
    w_acoustic: float,
) -> Tuple[float, List[str]]:
    """Scores the four original signals: genre, mood, energy proximity, acousticness."""
    score = 0.0
    reasons: List[str] = []

    if song.get("genre") == user_prefs.get("genre"):
        score += w_genre
        reasons.append(f"genre matches ({song['genre']})")

    if song.get("mood") == user_prefs.get("mood"):
        score += w_mood
        reasons.append(f"mood matches ({song['mood']})")

    if "energy" in user_prefs:
        energy_diff = abs(song["energy"] - user_prefs["energy"])
        score += (1 - energy_diff) * w_energy
        if energy_diff <= 0.15:
            reasons.append(f"energy closely matches ({song['energy']:.2f})")

    if user_prefs.get("likes_acoustic") and song["acousticness"] >= 0.6:
        score += song["acousticness"] * w_acoustic
        reasons.append(f"acoustic feel ({song['acousticness']:.2f})")

    return score, reasons


def _score_advanced_features(
    user_prefs: Dict,
    song: Dict,
    w_pop: float,
    w_decade: float,
    w_tags: float,
) -> Tuple[float, List[str]]:
    """Challenge 1: Scores popularity, release decade, mood tags, and instrumental preference."""
    score = 0.0
    reasons: List[str] = []

    popularity = float(song.get("popularity", 0))
    if popularity > 0:
        score += (popularity / 100.0) * w_pop
        if popularity >= 75:
            reasons.append(f"popular ({popularity:.0f}/100)")

    preferred_decade = user_prefs.get("preferred_decade", "")
    if preferred_decade and song.get("release_decade") == preferred_decade:
        score += w_decade
        reasons.append(f"from preferred era ({song['release_decade']})")

    preferred_tags = user_prefs.get("preferred_mood_tags", [])
    song_tags = song.get("mood_tags", [])
    if preferred_tags and song_tags:
        matched = [tag for tag in preferred_tags if tag in song_tags]
        if matched:
            score += (len(matched) / len(preferred_tags)) * w_tags
            reasons.append(f"mood tags: {', '.join(matched)}")

    if user_prefs.get("prefer_instrumental") and song.get("instrumental"):
        score += 0.5
        reasons.append("instrumental track")

    return score, reasons


def score_song(
    user_prefs: Dict,
    song: Dict,
    weights: Optional[Dict] = None,
    mode: str = "default",
) -> Tuple[float, str]:
    """
    Scores a single song against user preferences.
    Returns (score, explanation).

    Scoring signals:
      - Genre match:      strongest taste filter
      - Mood match:       emotional context
      - Energy proximity: (1 - |diff|) * scale — rewards closeness to target
      - Acoustic bonus:   only when likes_acoustic is True
      - Popularity:       normalized 0-1 contribution (Challenge 1)
      - Decade match:     rewards songs from a preferred release era (Challenge 1)
      - Mood tags:        partial credit for matching detailed descriptors (Challenge 1)
      - Instrumental:     bonus when user prefers instrumental tracks (Challenge 1)

    Pass a custom `weights` dict OR a `mode` string ("genre_first", "mood_first",
    "energy_focused", "default") to select a scoring strategy (Challenge 2).
    """
    if weights is None:
        weights = SCORING_MODES.get(mode, SCORING_MODES["default"])

    w_genre    = weights.get("genre", 3.0)
    w_mood     = weights.get("mood", 2.0)
    w_energy   = weights.get("energy_scale", 1.5)
    w_acoustic = weights.get("acoustic", 1.0)
    w_pop      = weights.get("popularity", 0.5)
    w_decade   = weights.get("decade", 1.0)
    w_tags     = weights.get("mood_tags", 1.5)

    base_score, base_reasons = _score_base_signals(
        user_prefs, song, w_genre, w_mood, w_energy, w_acoustic
    )
    adv_score, adv_reasons = _score_advanced_features(
        user_prefs, song, w_pop, w_decade, w_tags
    )

    score = base_score + adv_score
    reasons = base_reasons + adv_reasons
    explanation = "Because: " + ", ".join(reasons) if reasons else "Closest overall match"
    return score, explanation


def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    weights: Optional[Dict] = None,
    mode: str = "default",
) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py

    Scores every song, ranks by score descending, returns top k.
    Pass optional `weights` dict or `mode` string to select a scoring strategy
    (Challenge 2: "genre_first", "mood_first", "energy_focused", "default").
    """
    min_pop = float(user_prefs.get("min_popularity", 0))
    filtered = [s for s in songs if float(s.get("popularity", 0)) >= min_pop]

    scored = [(*score_song(user_prefs, song, weights, mode), song) for song in filtered]
    # scored items are (score, explanation, song) — repack as (song, score, explanation)
    results = [(song, score, expl) for score, expl, song in scored]
    results.sort(key=lambda x: x[1], reverse=True)
    return results[:k]


def recommend_with_diversity(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    weights: Optional[Dict] = None,
    mode: str = "default",
    artist_penalty: float = 0.7,
    genre_penalty: float = 0.85,
    max_per_genre: int = 2,
) -> List[Tuple[Dict, float, str]]:
    """
    Challenge 3: Diversity and Fairness Logic.

    Recommends songs with diversity penalties to prevent domination by
    a single artist or genre:
      - Artist penalty:  if an artist already appears in the ranked list,
        multiply their next song's score by `artist_penalty` (default 0.70,
        i.e., a 30% reduction).
      - Genre penalty:   if a genre appears `max_per_genre` or more times,
        multiply the next song's score by `genre_penalty` (default 0.85,
        i.e., a 15% reduction).

    The penalties are applied greedily in descending raw-score order, then the
    full penalized list is re-sorted so the final top-k reflects diversity.
    """
    min_pop = float(user_prefs.get("min_popularity", 0))
    filtered = [s for s in songs if float(s.get("popularity", 0)) >= min_pop]

    # Step 1: Score every song
    all_scored = []
    for song in filtered:
        raw_score, explanation = score_song(user_prefs, song, weights, mode)
        all_scored.append((song, raw_score, explanation))

    # Step 2: Sort by raw score so we process highest-scoring songs first
    all_scored.sort(key=lambda x: x[1], reverse=True)

    # Step 3: Apply diversity penalties in greedy order
    artist_counts: Dict[str, int] = {}
    genre_counts: Dict[str, int] = {}
    penalized: List[Tuple[Dict, float, str]] = []

    for song, raw_score, explanation in all_scored:
        artist = song.get("artist", "")
        genre  = song.get("genre", "")
        adjusted = raw_score
        notes: List[str] = []

        if artist_counts.get(artist, 0) > 0:
            adjusted *= artist_penalty
            notes.append(f"artist penalty x{artist_penalty}")

        if genre_counts.get(genre, 0) >= max_per_genre:
            adjusted *= genre_penalty
            notes.append(f"genre cap penalty x{genre_penalty}")

        full_explanation = explanation
        if notes:
            full_explanation += f" [Diversity: {'; '.join(notes)}]"

        penalized.append((song, adjusted, full_explanation))

        # Update counts so later songs in this loop see accurate history
        artist_counts[artist] = artist_counts.get(artist, 0) + 1
        genre_counts[genre]   = genre_counts.get(genre, 0) + 1

    # Step 4: Re-sort by penalized score and return top k
    penalized.sort(key=lambda x: x[1], reverse=True)
    return penalized[:k]
