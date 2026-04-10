# Reflection: Profile Pair Comparisons

This file documents how different user profiles produced different recommendations
and explains — in plain language — why the differences make sense (or don't).

---

## Pair 1: High-Energy Pop vs. Chill Lofi

**High-Energy Pop** wants pop music, a happy mood, and high energy (0.85).
**Chill Lofi** wants lofi music, a chill mood, and low energy (0.35) with acoustic preference.

These two profiles are nearly opposites, and the outputs reflect that perfectly.
High-Energy Pop's top song (*Sunrise City*) is a bright, fast pop track. Chill Lofi's
top song (*Library Rain*) is a slow, quiet lofi loop. Not a single song appears in both
top-5 lists. This makes total sense: genre + mood pull in completely different directions,
and even the energy scale (0.85 vs 0.35) ensures that whatever scores well for one profile
will score poorly for the other. The system behaves correctly here.

---

## Pair 2: High-Energy Pop vs. Deep Intense Rock

Both profiles want high energy (0.85 and 0.95), but they prefer different genres and moods.

The top-1 result differs: *Sunrise City* (pop/happy) for Pop, *Storm Runner* (rock/intense)
for Rock. However, from rank 2 onward, there is significant overlap — *Gym Hero* and
*Shatter Glass* appear in both lists because they match the high-energy dimension even
without matching genre. This shows the energy weight doing useful work: when genre has
already been rewarded for the #1 slot, high-energy songs rise together in the lower ranks.
The difference is logical — genre preference separates #1, but shared energy brings the
rest together.

---

## Pair 3: Chill Lofi vs. Adversarial (High-Energy + Sad)

**Chill Lofi** is a coherent profile — low energy, chill mood, acoustic preference.
**Adversarial High-Energy + Sad** is deliberately conflicted — it wants high energy (0.90)
but also a sad mood and acoustic sounds.

Chill Lofi's top 5 are all calm, quiet songs. The adversarial profile's #1 is
*Autumn Letters* (folk/sad/energy=0.33) — a quiet, slow track — even though the user
asked for energy=0.90. This is a system failure: the genre+mood bonus (+5.0) completely
overrides the massive energy mismatch. In plain terms, if you tell the app you love
intense music but are in a sad mood, it will serve you a folk ballad because "sad" is
the loudest signal in the scoring formula. The adversarial profile reveals that the
system cannot handle conflicting preferences gracefully.

---

## Pair 4: Default Weights vs. Experimental Weights (High-Energy Pop)

Using the same High-Energy Pop profile with two different weight configurations:

- **Default** (genre=3.0, energy_scale=1.5): *Gym Hero* (pop/intense) ranks #2 over
  *Rooftop Lights* (indie pop/happy). Genre matching (pop) pushes *Gym Hero* up even
  though its mood is wrong.
- **Experimental** (genre=1.5, energy_scale=3.0): *Rooftop Lights* climbs to #2,
  *Gym Hero* drops to #3. Why? *Rooftop Lights* has a closer energy (0.76 vs target 0.85)
  and matches the happy mood. With genre worth less, these signals matter more.

In plain language: when you make the system care twice as much about energy, songs that
"feel" right energetically move up — even if they're not exactly the right genre. The
recommendations become slightly more varied and arguably more accurate for a user whose
energy preference is just as important as genre taste.

---

## Pair 5: Adversarial (High-Energy + Sad) — Default vs. Experimental Weights

This is where the weight shift creates the biggest visible change.

- **Default**: Ranks 2–5 are all low-energy acoustic songs (*Dirt Road Summer*,
  *Coffee Shop Stories*, *Library Rain*, *Focus Flow*). The acoustic bonus dominates
  once the top genre+mood winner is decided.
- **Experimental**: Ranks 2–5 flip to high-energy songs (*Storm Runner*, *Gym Hero*,
  *Bass Cathedral*, *Golden Block*). Doubling the energy weight means the user's stated
  energy=0.90 preference finally shows up in the lower ranks.

This is a case where the experimental weights produce more logically consistent results:
if the user wants high energy, at least some high-energy songs should appear in the top 5,
even if the #1 winner is locked by genre+mood. The default configuration essentially
ignores the energy signal for this profile type, which is a hidden bias.

---

## Overall Takeaway

The recommender works reliably when user preferences are internally consistent (genre,mood, and energy all point in the same direction). It struggles when preferences conflict because the scoring formula has no way to trade off or balance competing signals — it just adds them up. Genre weight is strong enough to lock in a winner before energy gets a vote, which creates filter bubbles for users with small or single-song genres in the dataset. Doubling energy weight reduces this dominance and creates more variety, but it also means a song can rank highly purely on energy even when genre and mood are wrong — a different kind of mismatch. The right weight balance likely sits somewhere between the two configurations tested.
