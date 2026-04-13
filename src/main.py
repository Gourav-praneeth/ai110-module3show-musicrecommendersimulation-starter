"""
Music Recommender Simulation — All Challenges Demo.

Challenge 1: Advanced Song Features   — popularity, release_decade, mood_tags, instrumental, explicit
Challenge 2: Multiple Scoring Modes   — genre_first, mood_first, energy_focused strategies
Challenge 3: Diversity & Fairness     — artist/genre penalty prevents top-k monopolization
Challenge 4: Visual Summary Table     — tabulate for formatted, readable output
"""

try:
    from tabulate import tabulate as _tabulate
    HAS_TABULATE = True
except ImportError:
    HAS_TABULATE = False

try:
    from recommender import load_songs, recommend_songs, recommend_with_diversity, SCORING_MODES
except ModuleNotFoundError:
    from src.recommender import load_songs, recommend_songs, recommend_with_diversity, SCORING_MODES


# ---------------------------------------------------------------------------
# Profile name constants (avoids duplicated string literals)
# ---------------------------------------------------------------------------
PROFILE_HIGH_ENERGY_POP = "High-Energy Pop"
PROFILE_CHILL_LOFI      = "Chill Lofi"


# ---------------------------------------------------------------------------
# User profiles
# ---------------------------------------------------------------------------

# Original stress-test profiles (Challenge 1: now include new preference fields)
PROFILES = {
    PROFILE_HIGH_ENERGY_POP: {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.85,
        "likes_acoustic": False,
        "preferred_mood_tags": ["euphoric", "uplifting"],
        "min_popularity": 70,
    },
    PROFILE_CHILL_LOFI: {
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.35,
        "likes_acoustic": True,
        "prefer_instrumental": True,
        "preferred_mood_tags": ["focused", "mellow"],
    },
    "Deep Intense Rock": {
        "genre": "rock",
        "mood": "intense",
        "energy": 0.95,
        "likes_acoustic": False,
        "preferred_mood_tags": ["aggressive", "powerful"],
        "preferred_decade": "2010s",
    },
    # Adversarial: high energy but sad mood — conflicting signals
    "Adversarial (high energy + sad)": {
        "genre": "folk",
        "mood": "sad",
        "energy": 0.9,
        "likes_acoustic": True,
        "preferred_mood_tags": ["melancholic", "nostalgic"],
    },
    # Adversarial: genre that barely exists in dataset, calm energy
    "Adversarial (rare genre + mid energy)": {
        "genre": "jazz",
        "mood": "relaxed",
        "energy": 0.5,
        "likes_acoustic": True,
        "preferred_decade": "2010s",
    },
}

# Extra profiles that showcase the new Challenge 1 preference fields
CHALLENGE1_PROFILES = {
    "Nostalgic 2010s Listener": {
        "genre": "synthwave",
        "mood": "moody",
        "energy": 0.75,
        "likes_acoustic": False,
        "preferred_decade": "2010s",
        "preferred_mood_tags": ["nostalgic", "moody"],
    },
    "Study-Mode Instrumentalist": {
        "genre": "lofi",
        "mood": "focused",
        "energy": 0.40,
        "likes_acoustic": True,
        "prefer_instrumental": True,
        "preferred_mood_tags": ["focused", "mellow"],
        "min_popularity": 50,
    },
}


# ---------------------------------------------------------------------------
# Challenge 4: Visual Summary Table helper (tabulate)
# ---------------------------------------------------------------------------

def _truncate(text: str, max_len: int = 45) -> str:
    return text if len(text) <= max_len else text[: max_len - 1] + "…"


def print_table(title: str, recommendations: list) -> None:
    """Challenge 4: Display recommendations as a formatted ASCII table."""
    print(f"\n{'=' * 72}")
    print(f"  {title}")
    print(f"{'=' * 72}")

    rows = []
    for rank, (song, score, explanation) in enumerate(recommendations, 1):
        reason = explanation.replace("Because: ", "").replace("Closest overall match", "overall match")
        rows.append([
            rank,
            song["title"],
            song["artist"],
            song["genre"],
            f"{song['energy']:.2f}",
            f"{score:.2f}",
            _truncate(reason),
        ])

    headers = ["#", "Title", "Artist", "Genre", "Energy", "Score", "Reason"]

    if HAS_TABULATE:
        print(_tabulate(rows, headers=headers, tablefmt="grid"))
    else:
        # Simple ASCII fallback
        col_w = [max(len(str(r[i])) for r in [headers] + rows) for i in range(len(headers))]
        sep = "+-" + "-+-".join("-" * w for w in col_w) + "-+"
        def fmt_row(r):
            return "| " + " | ".join(str(v).ljust(w) for v, w in zip(r, col_w)) + " |"
        print(sep)
        print(fmt_row(headers))
        print(sep)
        for r in rows:
            print(fmt_row(r))
        print(sep)
    print()


# ---------------------------------------------------------------------------
# Runner helpers
# ---------------------------------------------------------------------------

def run_profile(name: str, user_prefs: dict, songs: list, weights: dict = None, mode: str = "default") -> None:
    label = f"{name}"
    if weights:
        label += " [custom weights]"
    elif mode != "default":
        label += f" [mode: {mode}]"
    recs = recommend_songs(user_prefs, songs, k=5, weights=weights, mode=mode)
    print_table(label, recs)


def run_with_diversity(name: str, user_prefs: dict, songs: list) -> None:
    print_table(f"{name} — NO diversity penalty", recommend_songs(user_prefs, songs, k=5))
    print_table(f"{name} — WITH diversity penalty", recommend_with_diversity(user_prefs, songs, k=5))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    songs = load_songs("data/songs.csv")

    if not HAS_TABULATE:
        print("\n[Tip] Install tabulate for prettier tables: pip install tabulate\n")

    # ------------------------------------------------------------------
    # Step 1 & 2: Stress test — default weights
    # (Challenge 1 preferences are active in the profiles above)
    # ------------------------------------------------------------------
    print("\n" + "#" * 72)
    print("# STEP 1 & 2: Stress Test — Default Weights (Challenge 1 features active)")
    print("#" * 72)
    for name, prefs in PROFILES.items():
        run_profile(name, prefs, songs)

    # ------------------------------------------------------------------
    # Step 3: Weight-Shift Experiment
    # ------------------------------------------------------------------
    print("#" * 72)
    print("# STEP 3: Weight-Shift Experiment (energy x2, genre /2)")
    print("#" * 72)
    shifted_weights = {"genre": 1.5, "mood": 2.0, "energy_scale": 3.0, "acoustic": 1.0,
                       "popularity": 0.5, "decade": 1.0, "mood_tags": 1.5}
    for name, prefs in PROFILES.items():
        run_profile(name, prefs, songs, weights=shifted_weights)

    # ------------------------------------------------------------------
    # Challenge 1: Advanced Features Demo
    # ------------------------------------------------------------------
    print("#" * 72)
    print("# CHALLENGE 1: Advanced Song Features")
    print("# New scoring signals: popularity, release_decade, mood_tags, instrumental")
    print("#" * 72)
    for name, prefs in CHALLENGE1_PROFILES.items():
        run_profile(name, prefs, songs)

    # ------------------------------------------------------------------
    # Challenge 2: Multiple Scoring Modes
    # ------------------------------------------------------------------
    print("#" * 72)
    print("# CHALLENGE 2: Multiple Scoring Modes — same profile, three strategies")
    print("#" * 72)
    demo_user = PROFILES[PROFILE_HIGH_ENERGY_POP]
    for mode_name in ("genre_first", "mood_first", "energy_focused"):
        run_profile(PROFILE_HIGH_ENERGY_POP, demo_user, songs, mode=mode_name)

    print("  Scoring mode weight tables:")
    mode_rows = [
        [m] + [f"{SCORING_MODES[m][k]:.1f}" for k in ("genre", "mood", "energy_scale", "popularity", "mood_tags")]
        for m in SCORING_MODES
    ]
    mode_headers = ["Mode", "genre", "mood", "energy", "popularity", "mood_tags"]
    if HAS_TABULATE:
        print(_tabulate(mode_rows, headers=mode_headers, tablefmt="simple"))
    else:
        for row in mode_rows:
            print("  ", "  ".join(str(v).ljust(14) for v in row))
    print()

    # ------------------------------------------------------------------
    # Challenge 3: Diversity & Fairness
    # ------------------------------------------------------------------
    print("#" * 72)
    print("# CHALLENGE 3: Diversity & Fairness Logic")
    print("# Artist penalty 0.70 (30% reduction), genre cap after 2 songs (15% reduction)")
    print("#" * 72)
    # "Chill Lofi" normally surfaces LoRoom twice (songs 2 & 9) — ideal for demonstrating the penalty
    run_with_diversity(PROFILE_CHILL_LOFI, PROFILES[PROFILE_CHILL_LOFI], songs)
    run_with_diversity(PROFILE_HIGH_ENERGY_POP, PROFILES[PROFILE_HIGH_ENERGY_POP], songs)

    # ------------------------------------------------------------------
    # Analysis
    # ------------------------------------------------------------------
    print("=" * 72)
    print("  ANALYSIS SUMMARY")
    print("=" * 72)
    print("  Challenge 1 — New features (popularity, decade, mood_tags, instrumental)")
    print("    reward tracks that match the user's preferred era and vibe descriptors,")
    print("    not just top-level genre/mood. Popular tracks get a small bonus.")
    print()
    print("  Challenge 2 — Switching modes shifts which signal dominates:")
    print("    genre_first  → genre match is 5x, cross-genre songs rarely surface")
    print("    mood_first   → mood tags drive 7.5 pts, emotional fit wins over genre")
    print("    energy_focus → energy proximity is 4x, nearest BPM/intensity wins")
    print()
    print("  Challenge 3 — Diversity penalty prevents artist/genre monopoly.")
    print("    Without it, LoRoom fills two of five Chill Lofi slots.")
    print("    With penalty, the second LoRoom song is pushed down by 30%,")
    print("    surfacing a more varied listen.")
    print()


if __name__ == "__main__":
    main()
