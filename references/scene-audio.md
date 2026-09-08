# Scene Audio — 场景声音

Sound for a scroll-driven scene: a music bed, an ambient world, and the noises the visitor's own hand
makes. All three are usually asked for at once, and they fight over the same few dB.

Nothing here is mixing theory. It is the set of things that were measured after being guessed wrong.

> Documented case (2026-08, heritage-ruins scroll scene): WebAudio, one music bed + wind/sand/earth ambience + 8 interaction
> sounds across 4 acts. Oracles: `scripts/audio-test.mjs`, `scripts/ambience-test.mjs`.

---

## §1 Three buses, because there are three complaints

The three notes that arrive together — 「加首 BGM」「交互音效太少」「氛围音听不清但也别吵」 — cannot be
served by one master fader. In the case project wind, sand, rammed earth **and** all seven interaction
sounds hung off `master`: turning the wind down turned the visitor's own hands down with it.

| bus | carries | governed by |
|---|---|---|
| `bgm` | the music bed | per-act curve (§2) + ducking (§3) |
| `hand` | everything the **visitor** caused | one trim, raised as a group |
| `master` | wind, sand, earth, birds, falling type — the world acting on its own | per-act ambience curve |

**The test for the `hand` bus is "did a person do this", not "where does it sound like it is".** A press
on a distant mound is thirty metres away and goes through the reverb — it is still a hand sound. Falling
type, a startled bird, a gust of sand are not, however close they sound.

One caveat that recurs: **a sustained layer needs its own trim after every bus change.** Raising `hand`
by +2.6 dB lifted a sustained low-frequency strain by +12.2 dB in the oracle and produced 「按钮的轰鸣」.
Short impulses just get clearer when a bus goes up; a sustained one becomes a hum pressed against the ear.
Its own gain went 2.4 → 1.15 → 0.85 while the bus went up. Re-trim sustained layers every time.

---

## §2 Balance is the relationship between the lines — never move two of them in opposite directions

Per-act curves, and the point is that they are **inverse**:

```
              ① paper   ② earth   ③ type   ④ empty
wind           0.30      1.00      0.16     0.42
music          0.60      0.46      0.86     0.76
→ measured    -33.9     -36.2     -30.8    -31.8   LUFS
```

Act ② is where the visitor stands in the desert and does things with their hands: wind full, music
underneath. Act ③ is where the type descends and there is nothing to do: wind almost gone, the act
handed to the music. Thick strings and wind occupy the same low-mid band — running both up is not "music
*and* wind", it is neither, plus it buries the interaction sounds sitting on top of that same band.

**The curve was re-cut three times. The middle version is the instructive one:**

| version | music trim | per-act music | measured LUFS | verdict |
|---|---|---|---|---|
| 1 | 0.596 | 0.40 / 0.25 / 1.00 / 0.80 | −37.8 / −41.8 / −29.8 / −31.7 | 「底乐太小」 |
| 2 | 0.85 | 0.72 / 0.58 / 1.00 / 0.90 | −29.6 / −31.4 / −26.7 / −27.6 | 「太大声，只能听见 bgm」 |
| 3 | 0.62 | 0.60 / 0.46 / 0.86 / 0.76 | −33.9 / −36.2 / −30.8 / −31.8 | ✓ |

Version 2 raised the music 8–10 dB **and** dropped the wind 5.7 dB in the same edit — a swing of more than
ten dB between the two lines, so of course only music remained.

> **Balance is a relationship. Move one line per iteration and re-measure, or you cannot attribute the
> result to anything.**

Print LUFS per act. "Sounds about right" is not a state you can return to next week.

### Source handling

Cut the music with a **stream copy**, never a re-encode (`ffmpeg -t 150 -c copy -map_metadata -1`), and do
every gain, fade and duck in a `GainNode` at runtime. The file stays bit-identical to the source; the mix
stays in code where it can be measured and reverted. A large-dynamic classical recording (measured
−25.3 LUFS, LRA 12.4) needs its trim chosen against the *whole* piece, not against its loudest bar.

---

## §3 Duck the bed under the hand — fast down, slow up

In the act where the music is fullest (−29.8 LUFS) the sound of brushing a single glyph peaked at
−35.0 dB: **the music covered the piece's primary interaction outright.** And that act's music cannot be
lowered — it is the emotional landing.

So the bed steps aside when a hand moves, and comes back slowly:

```js
duck = 0.45              // half a stop
tauDown = 0.05           // grab it immediately
tauUp   = 0.70           // return slowly enough that nobody hears the return
```

Hook it to the *hand* events only. A duck triggered by ambience is a pumping bed.

---

## §4 Add discrete events, not another continuous layer

The two halves of 「氛围音听不太清，但也不要只是风沙声不然也很吵」 sound contradictory and are the same
observation: a single low-passed noise bed has **no audible setting between "floor noise" and "noisy"**.
The ear tracks change, not level.

This is the same finding as the visual one where a hint could not be made brighter and had to be made to
*move* (`affordance.md` §11). The fix in both media is an event, not a level.

Everything added to the ambience was **discrete**, and hung off something already in the scene:

| event | acts | hook |
|---|---|---|
| sand grains | ② full, ④ 0.34, ③ 0.10, ① none | gust value, Poisson intervals |
| lark startled | ② | the bird the pointer already scares in the visuals |
| glyph landing | ③ | increments of the scatter progress, one per glyph |
| giant-glyph flip | ① | rising edge of the flip state |
| plate open / close | ② | the open/close calls, guarded so only the real transition fires |
| curtain descending | ③ | increments of the descent, one per column |

Result, measured with wind at a light gust: overall RMS **+0.1 dB** (no louder) while the zero-crossing
rate rose **+156 Hz** (brighter), and the sand's own peak sat **0.6 dB** below the wind's peak (audible).
Quieter overall and *more* legible.

---

## §5 A continuous quantity fed to a hand sound will be heard as ambience

Act ① had one interaction — dragging a fingertip to bring colour up through the paper — and it was silent,
on the reasoning that "ink bleeding into paper makes no sound". Half true: **the bleeding is silent, the
hand moving across the paper is not.** What is being voiced is the hand.

The first version was reported as 「①拍那个交互音太大，误以为是环境的沙沙声」. Turning it down fixed half
of it. Two faults, and the first is the root:

1. **It was fed the wrong quantity.** It took the wet field's density — which bleeds fast and dries slowly,
   so it **kept sounding after the hand stopped**. A sustained broadband noise cannot be voiced out of
   sounding like a floor, no matter how it is filtered. Feed **the distance travelled this frame**,
   accumulated into momentum with a fast decay (`e *= 0.62` per tick; the erase sound uses 0.72 — a stroke
   across paper has less follow-through than a scrub).
2. **It was filtered into a broadband.** A 900 Hz low-pass passes everything from 0 to 900 Hz — precisely
   the 「沙沙」 band. An 820 Hz **band-pass at Q 0.8** has a centre frequency, so it reads as a *scuff*
   rather than as noise.

And it must be timbrally separate from its neighbour or the next act reads as a repeat: erase is
**bright and crisp** (1150–2000 Hz), wash is **dull and low** (820 Hz).

### The REST oracle — run it on every hand sound

```
hand stops at T0 + 0.6 s; measure the window T0 + 0.85 → 1.1 s
fail if the level has not dropped ≥ 15 dB
```

Measured −18.6 dB after the fix. **Under 15 dB it will be heard as ambience**, regardless of volume.

Note the two criteria genuinely conflict: "silent the moment the hand stops" wants fast decay, "audible
while drawing" wants level — and fast decay drops the segment's RMS, which is how an intermediate version
ended up 7.5 dB below the wind ("buried"). The answer is not a compromise decay. **Keep the decay fast and
put the level back** (0.42 → 0.16 → 0.22).

---

## §6 The filter eats 10–20 dB. Look at the chain before you pick a number

The most-repeated mistake in the project, logged **four separate times in one file** and still made the
fourth time by ear.

Sand grains were authored at `force = 0.05` because "they should be very quiet". Measured: total RMS and
crest factor **did not move at all** — not quiet, *absent*. The reference number came from a brush impulse
at 0.28 through a band-pass at Q 1.1; the sand's band-pass is Q 2.4, **46% of the bandwidth**, so the same
number arrives ~7 dB lower. Corrected to 0.26–0.68. An identical error on a drop sound: 0.045 → 0.16.

> **Before writing a gain for any layer: read what filter it passes through.** A number copied from a
> layer with a different Q is not a number.

### Density and loudness are different complaints

"Can't hear the sand" was also measured as **2.7 grains/second** — one every 370 ms, which is "an
occasional tick", not "sand in the wind" — while a single grain peaked at −25.2 dB, only 3 dB under the
wind's peak. It was never a loudness problem. Re-authored as `(0.12 + g² × 1.7) × 26`: 4.6/s in light
wind, twenty-odd at a gust's peak.

---

## §7 Measuring: per-sample subtraction, on a deterministic render

Render the timeline offline twice with one layer switched off (`__noSand`) and **subtract sample by
sample**. Comparing the two renders' *aggregate statistics* reports +0.0 for everything — not because the
layer is silent, but because wind's own crest factor is 14 dB and swallows it.

This requires the whole render to be deterministic. Random sample offsets into a noise table shift every
later layer and destroy the subtraction — see `verification-harness.md` §3 for the failure (a 7.3 dB
phantom swing, one false alarm, one wrongly blamed layer) and the golden-ratio phaser that fixes it.

What to print per layer: **total RMS** (is it noisier), **zero-crossing rate** (is it brighter), **the
layer's own RMS and peak** after subtraction, and **events per second** for anything granular.

---

## §8 Checklist

- [ ] Separate `bgm` / `hand` / ambience buses; a hand sound is classified by who caused it
- [ ] Sustained layers re-trimmed individually after any bus change
- [ ] Per-act gain curves written down, LUFS printed per act
- [ ] One line moved per iteration; never two in opposite directions
- [ ] Music ducked by hand events only — fast attack, slow release
- [ ] Ambience enriched with **discrete events** hooked to things already in the scene, not a louder bed
- [ ] Every hand sound driven by a per-frame delta with fast decay, never by a persistent state value
- [ ] REST oracle ≥ 15 dB on every hand sound
- [ ] Neighbouring interactions timbrally distinct
- [ ] Every gain chosen after looking at the filter it passes through
- [ ] Granular layers checked for **density** as well as level
- [ ] Measurement is per-sample subtraction on a deterministic render
