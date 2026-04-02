from typing import List, Dict, Tuple, Optional
import csv
from dataclasses import dataclass

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

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        scored = [(song, self._score(user, song)) for song in self.songs]
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
        if reasons:
            return "Recommended because: " + ", ".join(reasons)
        return "Closest overall match based on genre, mood, and energy"

    def _score(self, user: UserProfile, song: Song) -> float:
        score = 0.0
        if song.genre == user.favorite_genre:
            score += 3.0
        if song.mood == user.favorite_mood:
            score += 2.0
        score += (1 - abs(song.energy - user.target_energy)) * 1.5
        if user.likes_acoustic:
            score += song.acousticness * 1.0
        return score


def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    songs = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["energy"] = float(row["energy"])
            row["tempo_bpm"] = float(row["tempo_bpm"])
            row["valence"] = float(row["valence"])
            row["danceability"] = float(row["danceability"])
            row["acousticness"] = float(row["acousticness"])
            songs.append(row)
    print(f"Loaded {len(songs)} songs from {csv_path}")
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, str]:
    """
    Scores a single song against user preferences.
    Returns (score, explanation).

    Scoring weights:
      - Genre match:   +3.0  (strongest taste signal)
      - Mood match:    +2.0  (emotional context)
      - Energy proximity: (1 - |song - user|) * 1.5  (rewards closeness, not extremes)
    """
    score = 0.0
    reasons = []

    if song.get("genre") == user_prefs.get("genre"):
        score += 3.0
        reasons.append(f"genre matches ({song['genre']})")

    if song.get("mood") == user_prefs.get("mood"):
        score += 2.0
        reasons.append(f"mood matches ({song['mood']})")

    if "energy" in user_prefs:
        energy_diff = abs(song["energy"] - user_prefs["energy"])
        energy_score = (1 - energy_diff) * 1.5
        score += energy_score
        if energy_diff <= 0.15:
            reasons.append(f"energy closely matches ({song['energy']:.2f})")

    if user_prefs.get("likes_acoustic") and song["acousticness"] >= 0.6:
        score += song["acousticness"] * 1.0
        reasons.append(f"acoustic feel ({song['acousticness']:.2f})")

    explanation = "Because: " + ", ".join(reasons) if reasons else "Closest overall match"
    return score, explanation


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py

    Scores every song, ranks by score descending, returns top k.
    """
    scored = [(*score_song(user_prefs, song), song) for song in songs]
    # scored items are (score, explanation, song) — repack as (song, score, explanation)
    results = [(song, score, explanation) for score, explanation, song in scored]
    results.sort(key=lambda x: x[1], reverse=True)
    return results[:k]
