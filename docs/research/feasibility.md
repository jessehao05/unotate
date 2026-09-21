# Feasibility Notes

Consolidated notes from architecture/feasibility discussion. Picks up from
[brainstorming.md](../brainstorming.md).

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

**Conclusion:** Python backend, but because of `music21`, not because of `torch`.

## Deployment risks in the original plan

1. **yt-dlp from a datacenter IP.** YouTube blocks/throttles cloud provider
   IP ranges (Render, Fly, Railway, etc.). Works in local dev, breaks in prod
   intermittently. Given personal-use scope: make file upload the primary
   path, treat URL input as best-effort.
2. **Render free tier is the wrong shape.** ~512MB RAM, spins down after
   idle (verify current limits). PyTorch + checkpoint likely won't fit
   comfortably; cold start + CPU inference could mean minutes for first
   request. Better free options: Hugging Face Spaces (generous CPU tier,
   built for this) or Modal (serverless, real GPUs, monthly free credit).
3. **Sync request/response won't hold** for multi-minute jobs. Use
   `POST /jobs` → `202 {job_id}` → poll `GET /jobs/{id}` instead of a long
   held HTTP request.

## Output format

Prefer **MusicXML** over `.mscz` (MuseScore's native format is
version-coupled/tool-specific; MusicXML opens everywhere — MuseScore,
Dorico, Sibelius, Finale, Flat.io). Always also hand back the raw **MIDI**
alongside it — free to produce, and it's the fallback when notation comes
out wrong. Skip PNG except as an in-browser preview.

## Repertoire-specific difficulty (Liszt Liebesträume No. 3 solo; BELLA&LUCAS-style 4-hand duets)

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

**Model choice:** use the ByteDance high-resolution piano transcription
model (Kong et al., "High-resolution Piano Transcription with Pedals by
Regressing Onsets and Offsets Times") over Basic Pitch — it's trained on
MAESTRO (close to this repertoire) and predicts sustain pedal explicitly,
addressing the offset-ambiguity problem. Check whether a transformer
successor (e.g. hFT-Transformer) has since overtaken it on MAESTRO
benchmarks.

**4-hand duets:** which player played which note is **not acoustically
recoverable** from a single mixdown — not a model-quality problem, the
information isn't in the signal (Primo/Secondo overlap in register
constantly). Target a **condensed 2-stave score** of everything sounding;
treat Primo/Secondo splitting as manual work in MuseScore. Also expect
graceful-not-total degradation from 10–16 simultaneous notes vs. MAESTRO's
solo-piano distribution.

## University GPU cluster

- **Helps:** running larger/better models without footprint worry,
  batch-evaluating a corpus, fine-tuning if that's ever pursued.
- **Doesn't help:** the notation stage (quantization, key detection, staff
  assignment, MusicXML generation) — that's symbolic CPU work, and it's
  where the actual quality problem lives.
- **Can't do:** host the backend. Clusters are SLURM batch schedulers (job
  + queue, not a persistent HTTP endpoint), typically VPN-gated, and running
  a public web service on institutional research compute is likely against
  acceptable-use policy.

Net effect: reinforces building the core as a plain Python **library + CLI**
first (device/model selection behind config), so the same code runs locally
for iteration and on the cluster for batch jobs, with a web layer as an
optional later wrapper.

## Evaluation strategy (free ground truth)

Liebesträume is public domain (1850) — clean engravings exist on IMSLP.
Splits the two example pieces into distinct roles:

- **Liszt = evaluation set.** A score already exists, so transcribing it has
  no product value, but it gives an objective accuracy measurement.
- **4-hand arrangements = the actual product.** No published score — that's
  why the tool is worth building.

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
  rendering) + Tone.js (playback) + Zustand frontend. Deployed on HF Spaces
  (backend) + Vercel (frontend) — validates that combination independently.
- **ML pipeline:** BS-RoFormer + Demucs for source separation; YourMT3+
  ensembled with ByteDance piano transcription + BiLSTM refinement for
  transcription. Claims 96.1% F1 on MAESTRO test set — but this is
  note-level onset F1 on studio solo-piano recordings; says nothing about
  notation readability or performance on compressed YouTube rips of 4-hand
  arrangements. Don't let the headline number reset expectations.
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
  multi-instrument support, the collaborative editor, and account plumbing.
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
  core/          Python library, no web deps
    ingest       yt-dlp / file upload → ffmpeg → normalized wav
    transcribe   ByteDance model (device: cpu|cuda) → MIDI + pedal
    rhythm       beat/tempo estimation → quantization  ← hardest stage
    engrave      key detect, hand split, music21 → MusicXML
  cli/           unotate transcribe <input> -o out.musicxml
  eval/          mir_eval + MV2H against IMSLP/MAESTRO ground truth
  web/           added last, thin FastAPI wrapper (HF Spaces)
```

Design calls favored given the repertoire:

- **Make the rhythm stage interactive, not fully automatic** — let the user
  supply tempo/meter/pickup, with automatic estimation as default. Full
  automation will lose to rubato; a manual override costs little and is
  the difference between unusable and useful for a personal tool.
- **Always emit raw unquantized MIDI alongside the MusicXML** — when
  notation comes out wrong (it will, on Liszt), MIDI preserves what the
  model actually heard so the notation stage can be re-run with different
  parameters without re-running inference.

## Open questions (unresolved as of this note)

1. **Is hosted deployment (Vercel + backend host) a hard requirement, or
   just the default assumption from the original brainstorm?** This
   determines whether `web/` is real early work or a later footnote. The
   cluster doesn't answer this — it can't host a persistent service anyway.
2. **Willing to accept upload-only input** (skip YouTube URL fetching
   server-side) to dodge the datacenter-IP blocking problem? Could still do
   the URL→audio download client-side/locally and only send audio to the
   backend.

Suggested next step (not yet started): build `core/` as a standalone
library + CLI, validate the pipeline on MAESTRO ground-truth MIDI first
(zero-inference baseline for the notation stage), then layer in real
transcription, then decide on `web/` once the above questions are answered.
