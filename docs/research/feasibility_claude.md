# Feasibility Notes

Consolidated notes from architecture/feasibility discussion. Picks up from
[overview.md](../overview.md).

> **Status (`solo/local` branch):** the overview now fixes scope to a
> **local CLI** (`unotate transcribe <url-or-file> -o out.musicxml`), **solo
> piano only**, **MusicXML output**. No web frontend, no hosted deployment,
> no 4-hand duets. Sections below are updated to match; earlier versions
> are in git history.

## Is Python required?

Not for the whole pipeline, but effectively yes for one stage:

| Stage | Python-locked? | Notes |
|---|---|---|
| YouTube → audio | No | `yt-dlp` CLI, ffmpeg — callable from anything |
| Audio → MIDI | No | Basic Pitch ships as TF.js (`@spotify/basic-pitch`), runs in-browser; ONNX models run under `onnxruntime-node`/WASM |
| MIDI → readable notation | **Yes, effectively** | The real lock-in — see below |
| MusicXML → PDF/PNG | No | MuseScore CLI / LilyPond / Verovio are native binaries |

The notation stage needs beat/tempo tracking, quantization to a grid, key
detection, and hand/staff splitting to turn a raw note list into something
legible. Python has `music21` + `librosa`/`madmom` for this. JS/TS has parsers
(`@tonejs/midi`) and renderers (OpenSheetMusicDisplay, VexFlow) but nothing
that does the musical analysis in between — you'd be writing that yourself.

**Conclusion:** Python, because of `music21`, not because of `torch`. With
the CLI-only scope there's no frontend, so the whole project can be Python.

## Running locally (replaces "Deployment risks")

The earlier hosting risks (Render's free-tier limits, YouTube blocking
datacenter IPs, needing an async job API for multi-minute requests) no
longer apply: everything runs on the user's machine.

What's left:

- **yt-dlp still breaks periodically** when YouTube changes its site, even
  from a home IP. Keep it updated (or unpinned), and keep local file input
  as the reliable path.
- **Long runs are fine** for a CLI, but print stage progress so a
  multi-minute transcription doesn't look hung.

## Output format

Prefer **MusicXML** over `.mscz` (MuseScore's native format is
version-coupled/tool-specific; MusicXML opens everywhere — MuseScore,
Dorico, Sibelius, Finale, Flat.io). If an `.mscz` is wanted, convert the
MusicXML with the MuseScore CLI rather than generating it directly. Always
also write the raw **MIDI** alongside it — free to produce, and it's the
fallback when notation comes out wrong. No PNG output.

## Repertoire-specific difficulty (Liszt Liebesträume No. 3, solo)

Note *detection* is the easy part — modern piano AMT is strong on
Romantic-era solo repertoire (in-domain for MAESTRO-trained models).
Notation is where it breaks, for three specific reasons:

- **Rubato.** Liebesträume has heavy tempo fluctuation. Beat trackers are
  trained mostly on steady tempo. If beat tracking drifts, quantization
  snaps to the wrong grid even with perfect note detection — an independent
  failure mode from note detection accuracy.
- **Hand/staff assignment.** Naive pitch-threshold splitting (< middle C →
  bass clef) fails on exactly this piece: melody sits in the middle
  register played by the thumb, with arpeggios both above and below,
  alternating hands. There's real research here (Nakamura et al., HMM-based
  hand separation from piano MIDI) — worth a look, not a heuristic to dash
  off. Three-stave cadenza passages won't be reproduced automatically by
  anything.
- **Pedal.** Heavy sustain makes note *offsets* genuinely ambiguous, not
  just hard to detect — directly affects duration/tie correctness.

**Model choice:** superseded by [models.md](models.md) (checked
2026-10-01). Short version: Transkun or the ByteDance/Kong model for audio →
MIDI (both predict sustain pedal, which addresses the offset-ambiguity
problem), PM2S for MIDI → score, and the Penner & Hindle pipeline (Kong →
hand separation → PM2S → MusicXML) as a reference implementation. Also try
Aria-AMT on lower-quality YouTube audio.

**4-hand duets:** out of scope on this branch.

## University GPU cluster

- **Helps:** running larger/better models without footprint worry,
  batch-evaluating a corpus, fine-tuning if that's ever pursued.
- **Doesn't help:** the notation stage (quantization, key detection, staff
  assignment, MusicXML generation) — that's symbolic CPU work, and it's
  where the actual quality problem lives.

Net effect: build the core as a plain Python **library + CLI** (device/model
selection behind config), so the same code runs locally for iteration and
on the cluster for batch evaluation jobs.

## Evaluation strategy (free ground truth)

Liebesträume is public domain (1850) — clean engravings exist on IMSLP, as
do scores for the other example pieces (Chopin nocturnes, Beethoven
sonatas). Any of them can serve as an evaluation set with an objective
accuracy measurement.

With duets dropped, the evaluation pieces and the pieces the tool is
actually used on are now the same kind of music. The earlier split
("Liszt = evaluation, 4-hand arrangements = product, since they have no
published score") no longer holds. The tool's main use is now solo YouTube
covers with no published score, so the classical pieces become proxy
evaluation sets (see "Resolved questions" below).

Two evaluation levels (verify current state/APIs of both before relying on
them):
- Note-level onset/offset F1 via `mir_eval`'s transcription module.
- Notation-aware comparison: MV2H (McLeod — multi-pitch/voice/meter/
  note-value/harmony) and/or `musicdiff` (compares music21 scores directly).
  Note-level F1 alone is misleading — it can look excellent while the
  notation is unusable.

## Prior art: rescored (github.com/calebyhan/rescored, rescored.vercel.app)

MIT-licensed, close analogue of this project. Key findings from reading the
repo (as of this research; verify current state before relying on details):

- **Stack:** FastAPI + Celery + Redis backend; React + VexFlow (notation
  rendering) + Tone.js (playback) + Zustand frontend, hosted on HF Spaces +
  Vercel. Not relevant to unotate's CLI-only scope.
- **ML pipeline:** BS-RoFormer + Demucs for source separation; YourMT3+
  ensembled with ByteDance piano transcription + BiLSTM refinement for
  transcription. Claims 96.1% F1 on MAESTRO test set — but this is
  note-level onset F1 on studio solo-piano recordings; says nothing about
  notation readability or performance on compressed YouTube rips. Don't let
  the headline number reset expectations.
- **Notation stage was abandoned.** Roadmap: Phase 1 (done) = transcription,
  separation, interactive editor, **MIDI export**. Phase 2 (not started) =
  multi-instrument, **grand staff**, **PDF export**. Code comment in
  `tasks.py`: *"Pipeline already returns MIDI path, no need for MusicXML
  generation"*; `app_config.py` marks a tie-notation flag as *"Deprecated
  (was only used by old generate_musicxml)"*. There was a music21 MusicXML
  path; it was retired in favor of MIDI + a manual VexFlow-based editor.
  This independently confirms hand/staff-splitting (grand staff) is the hard
  unsolved part.
- **Their own `docs/research/challenges.md` admissions** (useful, if
  somewhat stale in spots — describes basic-pitch/Demucs timings even
  though the README says YourMT3+/BS-RoFormer, so treat as design-era
  reasoning not current spec):
  - "Rachmaninoff: Many notes, complex voicing → accuracy drops to ~60%" —
    same texture class as Liebesträume.
  - "Users will need to edit ~20-40% of notes for complex music"; elsewhere
    "70-80% accuracy at best."
  - Rubato → "weird note durations"; grace notes detected as full notes.
  - Time signature: MIDI output has none, music21 guesses and is "often
    wrong" → mitigation is default to 4/4 and let user override.
  - Key detection "isn't always accurate" → default to C major, let user
    override.
  - Both mitigations collapse to "let the user set it manually" — matches
    the interactive-rhythm-stage idea below.
- **Dependency fragility signal:** `requirements.txt` has madmom commented
  out as "DISABLED: Incompatible with numpy 2.x," replaced with essentia.
  Beat-tracking libraries are the fragile part of this stack.
- **Codebase shape note:** `backend/pipeline.py` is ~103KB in a single file.

### What to borrow vs. skip from rescored

- **Skip:** source separation (BS-RoFormer/Demucs) — not needed since scope
  is piano-only, no other instruments. Their own docs cost this at 8-15 min
  on CPU; it's the slowest stage and a source of bleed artifacts. Also skip
  multi-instrument support, the web frontend/editor, and account plumbing.
- **Borrow (deliberately, not a fork):** the YourMT3+ / ByteDance ensemble
  model choice; their beat-synchronous quantization approach
  (`pipeline.py` `beat_synchronous_quantize`); their sustain-artifact /
  ghost-note merging logic (velocity envelope analysis for fading sustained
  notes misread as new onsets) — addresses a real failure mode worth not
  hitting blind. MIT license permits reuse; keep the notice.

## Reframed scope

**Audio → MIDI is commoditized. MIDI → readable grand-staff notation is
not.** Both this project and rescored's value lives in the second half;
rescored deferred it entirely. This means unotate is best scoped as *the
notation project*, with transcription as a thin, swappable stage rather
than the centerpiece.

This reframing has a methodological payoff: the notation stage can be built
and evaluated **without running any inference at all**, by using MAESTRO's
aligned ground-truth MIDI as input (isolates notation-stage error from
transcription error), then introducing real transcription output afterward
to see how much quality degrades. Debugging the two error sources
separately is the difference between a tractable project and guessing.

## Proposed architecture sketch

```
unotate/
  core/          Python library
    ingest       yt-dlp (URL) / local file → ffmpeg → normalized wav
    transcribe   Transkun or Kong (device: cpu|cuda) → MIDI + pedal
    rhythm       beat/tempo estimation → quantization  ← hardest stage
    engrave      key detect, hand split, music21 → MusicXML
  cli/           unotate transcribe <url-or-file> -o out.musicxml
  eval/          mir_eval + MV2H against IMSLP/MAESTRO ground truth
```

Design calls favored given the repertoire:

- **Make the rhythm stage user-overridable, not fully automatic** — let the
  user supply tempo/meter/pickup (CLI flags, e.g. `--tempo`, `--meter`),
  with automatic estimation as default. Full
  automation will lose to rubato; a manual override costs little and is
  the difference between unusable and useful for a personal tool.
- **Always emit raw unquantized MIDI alongside the MusicXML** — when
  notation comes out wrong (it will, on Liszt), MIDI preserves what the
  model actually heard so the notation stage can be re-run with different
  parameters without re-running inference.

## Resolved questions

- **Hosted deployment?** No. The project is a local CLI, so there's no
  `web/` layer.
- **Upload-only input to avoid datacenter-IP blocking?** Not needed. yt-dlp
  runs on the user's own connection, so URL input stays.
- **What's the tool for, now that duets are out?** Mainly **solo piano
  YouTube covers with no published score**. Consequences:
  - Real use has no ground truth, so evaluation relies on proxies:
    published classical scores, purchased or hand-made scores for a few
    covers, and synthetic audio rendered from pop-piano MIDI datasets.
  - Recording conditions (home/digital pianos, phone mics, reverb,
    compression) are the main transcription risk, so test models on
    YouTube-like audio, not just MAESTRO, and include Aria-AMT.
  - Pop/film/anime cover textures (melody in the right hand, accompaniment
    in the left, steadier tempo) are usually easier to notate than Liszt;
    Liebesträume becomes a stress test rather than the main target.

Suggested next step (not yet started): build `core/` as a standalone
library + CLI, validate the pipeline on MAESTRO ground-truth MIDI first
(zero-inference baseline for the notation stage), then layer in real
transcription.
