# Model Card: Music Recommender Simulation

## 1. Model Name

**GrooveMatch 1.0**

---

## 2. Intended Use

GrooveMatch 1.0 is designed to suggest songs from a small catalog that fit a user's musical taste profile. It is built for classroom exploration — not production use. The system assumes users can clearly express a single favorite genre, a single mood preference, a target energy level (0 to 1), and whether or not they enjoy acoustic-sounding music. It is not designed for real streaming platforms or for users with complex, mixed, or evolving taste.

---

## 3. How the Model Works

The recommender scores every song in the catalog against the user's stated preferences, then returns the top five highest-scoring songs.

Four things determine the score:

1. **Genre match** — if the song's genre matches the user's favorite genre, it gets the biggest point bonus (+3.0). This is the single most powerful signal.
2. **Mood match** — if the song's mood matches the user's favorite mood, it gets a moderate bonus (+2.0).
3. **Energy proximity** — the closer the song's energy level is to the user's target, the higher the bonus. A perfect energy match adds +1.5; a completely wrong energy adds nothing.
4. **Acoustic bonus** — if the user likes acoustic music and the song has a high acousticness score, a small extra bonus is added.

The four scores are simply added together. No learning or historical data is involved — every recommendation is calculated fresh from the rules above.

---

## 4. Data

The catalog contains **18 songs**, each described by 10 attributes: a unique ID, title, artist name, genre, mood label, energy (0–1 float), tempo in BPM, valence, danceability, and acousticness.

Genres represented: pop, lofi, rock, ambient, jazz, synthwave, indie pop, hip-hop, r&b, classical, country, electronic, metal, reggae, folk.

Moods represented: happy, chill, intense, focused, relaxed, moody, energetic, romantic, melancholic, nostalgic, uplifting, sad.

Most genres and moods have only **one song** each in the dataset. Pop and lofi have two songs each; every other genre is represented by a single track. This makes the catalog extremely sparse. Entire taste spaces — such as Latin, K-pop, soul, blues, or punk — are completely missing, and the dataset skews toward Western popular genres.

---

## 5. Strengths

The system works best when the user has a well-defined preference that matches a moderately represented genre. For example, a "High-Energy Pop" profile (pop, happy mood, energy 0.85) reliably surfaces *Sunrise City* at rank 1 with a strong score because genre, mood, and energy all align at once. Similarly, the "Chill Lofi" profile surfaces both lofi tracks (*Library Rain* and *Midnight Coding*) near the top, and the acoustic bonus correctly rewards those naturally quiet recordings. The scoring logic is transparent — every point can be traced back to a single rule — which makes the system easy to debug and explain.

---

## 6. Limitations and Bias

The scoring system has a strong **genre-dominance bias**: a genre match unconditionally awards +3.0 points, which is double the maximum energy contribution (+1.5 at perfect match). This means a genre-matching song with completely wrong energy will almost always outscore a genre-mismatching song with perfect energy — effectively overriding the user's energy preference whenever a genre hit exists. The small 18-song dataset amplifies this problem because genres such as rock, metal, jazz, country, reggae, and classical each have only **one representative song**, guaranteeing that genre-matching users are always served the same single track at the top no matter how mismatched its mood or energy is.

The **acoustic bonus is one-directional**: users who like acoustic tracks receive extra score, but users who explicitly dislike acoustic music get no penalty for high-acousticness songs appearing in their results — making the system subtly biased toward acoustic listeners.

Finally, both **genre and mood matching are strictly binary** — "happy" and "uplifting," or "chill" and "relaxed," receive zero partial credit — so emotionally adjacent moods produce the same zero contribution as completely unrelated ones, causing counterintuitive ranking failures for edge-case profiles.

---

## 7. Evaluation

We tested five user profiles with both default weights and an experimental weight configuration (energy ×2, genre ÷2):

| Profile | Genre | Mood | Energy | Acoustic |
|---|---|---|---|---|
| High-Energy Pop | pop | happy | 0.85 | No |
| Chill Lofi | lofi | chill | 0.35 | Yes |
| Deep Intense Rock | rock | intense | 0.95 | No |
| Adversarial: High-Energy + Sad | folk | sad | 0.90 | Yes |
| Adversarial: Rare Genre + Mid-Energy | jazz | relaxed | 0.50 | Yes |

**What we looked for:** Whether the top-ranked song felt intuitive for the profile, whether the same songs kept dominating, and how rankings shifted when weights changed.

**What worked well:** Standard profiles produced sensible results. *Sunrise City* ranked first for High-Energy Pop (score 6.46, matching genre + mood + energy). *Library Rain* and *Midnight Coding* both surfaced correctly for Chill Lofi. The recommender clearly understands well-defined profiles.

**What surprised us:** The adversarial "High-Energy + Sad" profile exposed the most striking failure. Despite the user targeting energy=0.90, *Autumn Letters* (energy=0.33 — a quiet folk song) ranked #1 because the genre and mood match combined for +5.0 points, easily overcoming the massive energy gap. A user who wants driving, intense music but expressed a sad mood would be served the opposite of what they likely want.

**Weight-shift experiment findings:** Doubling energy weight and halving genre weight caused the Chill Lofi top-5 to diversify — *Spacewalk Thoughts* (ambient, not lofi) climbed to rank 3 purely on energy proximity. For the adversarial sad profile, high-energy songs (*Storm Runner*, *Gym Hero*) replaced acoustic songs in ranks 2–5, confirming that genre weight is the primary driver of "sameness" in the default configuration. The change made recommendations more varied but not always more accurate.

---

## 8. Ideas for Improvement

1. **Partial credit for related genres and moods.** Instead of a binary match, define a similarity map (e.g., "chill" is 0.6 similar to "relaxed", "lofi" is 0.5 similar to "ambient") and award fractional points. This would eliminate the counterintuitive cliff between adjacent moods.

2. **Expand the song catalog significantly.** With only one song per niche genre, the system cannot generate meaningful variety. Adding at least 10–20 songs per genre would let the energy and mood dimensions actually differentiate results within a genre.

3. **Add an anti-repetition or diversity re-ranking step.** After scoring, check whether the top 5 results all share the same genre or artist and intentionally inject variety from lower-ranked but high-quality alternatives. This would make the list feel less repetitive for users whose favorite genre dominates the catalog.

---

## 9. Personal Reflection

Building GrooveMatch 1.0 made it clear that even a simple point-based system can *feel* surprisingly intelligent — until you probe the edges. Seeing *Sunrise City* correctly appear at rank 1 for a pop/happy/high-energy profile felt satisfying, as if the system "understood" the user. But the adversarial profiles immediately broke that illusion: *Autumn Letters*, a quiet folk ballad, topped the chart for a user who wanted loud, intense music, purely because two labels matched. That moment was the biggest lesson: a recommender can look good on average while quietly failing on the cases that matter most.

Using AI tools to help draft scoring logic and write test profiles was genuinely useful, but I had to double-check every suggestion against the actual code. AI-generated explanations were sometimes too confident about how the weights interacted, and a couple of suggested test cases assumed moods existed in the dataset that didn't. It reinforced that AI is a helpful co-pilot, not a replacement for reading the data yourself.

The most surprising thing was how much the *weight ratio* mattered compared to absolute values. Changing genre from 3.0 to 1.5 (while doubling energy) didn't just tweak rankings — it restructured the entire output for sparse genres. A single number sitting at the top of a scoring function can silently dominate thousands of recommendations before anyone notices.

If I extended this project, I would collect real listening history from a handful of people to see whether the genre-first assumption holds — or whether energy and mood are actually more predictive of what someone wants to hear next. My guess is that context (time of day, activity) matters more than any static profile, and that would be the next dimension worth modeling.

---
