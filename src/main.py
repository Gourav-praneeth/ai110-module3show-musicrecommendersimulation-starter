"""
Command line runner for the Music Recommender Simulation.
Runs stress tests with diverse user profiles and a weight-shift experiment.
"""

try:
    from recommender import load_songs, recommend_songs
except ModuleNotFoundError:
    from src.recommender import load_songs, recommend_songs


# ---------------------------------------------------------------------------
# Step 1: Diverse user profiles (including adversarial edge cases)
# ---------------------------------------------------------------------------

PROFILES = {
    "High-Energy Pop": {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.85,
        "likes_acoustic": False,
    },
    "Chill Lofi": {
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.35,
        "likes_acoustic": True,
    },
    "Deep Intense Rock": {
        "genre": "rock",
        "mood": "intense",
        "energy": 0.95,
        "likes_acoustic": False,
    },
    # Adversarial: high energy but sad mood — conflicting signals
    "Adversarial (high energy + sad)": {
        "genre": "folk",
        "mood": "sad",
        "energy": 0.9,
        "likes_acoustic": True,
    },
    # Adversarial: genre that barely exists in dataset, calm energy
    "Adversarial (rare genre + mid energy)": {
        "genre": "jazz",
        "mood": "relaxed",
        "energy": 0.5,
        "likes_acoustic": True,
    },
}


def run_profile(name: str, user_prefs: dict, songs: list, weights: dict = None) -> None:
    recommendations = recommend_songs(user_prefs, songs, k=5, weights=weights)
    label = f"  Profile: {name}"
    if weights:
        label += " [EXPERIMENTAL WEIGHTS]"
    print("=" * 60)
    print(label)
    print("=" * 60)
    for rank, rec in enumerate(recommendations, 1):
        song, score, explanation = rec
        print(f"  {rank}. {song['title']} ({song['genre']}, {song['mood']}, energy={song['energy']:.2f})")
        print(f"     Score: {score:.2f} | {explanation}")
    print()


def main() -> None:
    songs = load_songs("data/songs.csv")
    print()

    # ------------------------------------------------------------------
    # Step 1 & 2: Run all profiles with default weights
    # ------------------------------------------------------------------
    print("### STEP 1 & 2: Stress Test — Default Weights ###\n")
    for name, prefs in PROFILES.items():
        run_profile(name, prefs, songs)

    # ------------------------------------------------------------------
    # Step 3: Weight-Shift Experiment
    #   Original: genre=3.0, mood=2.0, energy_scale=1.5, acoustic=1.0
    #   Shifted:  genre=1.5 (halved), mood=2.0, energy_scale=3.0 (doubled), acoustic=1.0
    # ------------------------------------------------------------------
    print("### STEP 3: Weight-Shift Experiment (energy x2, genre /2) ###\n")
    experimental_weights = {
        "genre": 1.5,
        "mood": 2.0,
        "energy_scale": 3.0,
        "acoustic": 1.0,
    }

    for name, prefs in PROFILES.items():
        run_profile(name, prefs, songs, weights=experimental_weights)

    # ------------------------------------------------------------------
    # Analysis note
    # ------------------------------------------------------------------
    print("=" * 60)
    print("  ANALYSIS")
    print("=" * 60)
    print("  Default weights: genre=3.0, energy_scale=1.5")
    print("  Experimental:    genre=1.5, energy_scale=3.0")
    print()
    print("  Observation: With doubled energy weight, songs whose")
    print("  energy closely matches the user's target float higher,")
    print("  even when their genre doesn't match. Halving genre weight")
    print("  means a genre match alone is less decisive — variety")
    print("  increases for broad-energy profiles (e.g. Chill Lofi).")
    print()
    print("  Adversarial profiles (high energy + sad mood) expose that")
    print("  mood and genre can pull rankings in opposite directions,")
    print("  causing mid-energy songs to surface unexpectedly.")
    print()


if __name__ == "__main__":
    main()
