"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

try:
    from recommender import load_songs, recommend_songs
except ModuleNotFoundError:
    from src.recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv")

    # User taste profile — target values for genre, mood, energy, and acoustic preference.
    # genre and mood are matched exactly; energy uses proximity scoring.
    # Change these values to test different listener types.
    user_prefs = {
        "genre": "pop",          # favorite genre (e.g. "pop", "hip-hop", "lofi")
        "mood": "happy",         # favorite mood  (e.g. "happy", "chill", "intense")
        "energy": 0.8,           # target energy on a 0.0–1.0 scale
        "likes_acoustic": False, # bonus weight for acoustic tracks
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\nTop recommendations:\n")
    for rec in recommendations:
        # You decide the structure of each returned item.
        # A common pattern is: (song, score, explanation)
        song, score, explanation = rec
        print(f"{song['title']} - Score: {score:.2f}")
        print(f"{explanation}")
        print()


if __name__ == "__main__":
    main()
