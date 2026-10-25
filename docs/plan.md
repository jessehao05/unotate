# Plan (`solo/local`)

Goal: `unotate transcribe <url-or-file> -o out.musicxml` turns a solo piano
cover (YouTube or Instagram) into MusicXML + MIDI good enough to clean up in
MuseScore. Main use: covers with no published score.

Background: [overview.md](overview.md),
[feasibility_claude.md](research/feasibility_claude.md),
[models.md](research/models.md), [data.md](research/data.md).

Machine: Apple M1, 8 GB RAM, no CUDA. Inference runs on CPU (MPS later).

## Pipeline

```
ingest → transcribe → clean → rhythm → engrave → out.musicxml + out.mid
```

1. **ingest**: URL (yt-dlp) or local file → ffmpeg → mono wav; `--start/--end` trimming
2. **transcribe**: audio → performance MIDI + pedal (Transkun / Kong / Aria-AMT)
3. **clean**: remove ghost notes, sustain artifacts, very short notes
4. **rhythm**: beats, tempo, meter, quantization; `--tempo/--meter` overrides
5. **engrave**: key, hand/staff split, voices, spelling → MusicXML (start from PM2S)

Each stage writes its output to disk so later stages can be re-run without
re-running inference.

## Steps

### 0. Environment
- [ ] `brew install uv ffmpeg`
- [ ] `uv init --package --python 3.11`, `uv add yt-dlp`
- [ ] Add `data/` to `.gitignore` (audio is copyrighted, stays local)

### 1. Starter test set
- [ ] Download 5 clips from [data.md](research/data.md) to `data/raw/`:
  - Hampstead, TutorialsByHugo (ground truth)
  - Tong Hua, djjedforce (ground truth)
  - Hampstead, Sing2Piano (same song, different arranger/piano)
  - call of silence, gentle_motif (heavy reverb/pedal)
  - one Instagram reel (checks Instagram download works)
- [ ] Note what form the ground truth is in (PDF / MusicXML / MIDI)

### 2. Model bake-off
- [ ] Run Transkun, Kong, then Aria-AMT (may not fit in 8 GB) on all 5 clips → `data/out/<model>/<clip>.mid`
- [ ] Listen to / inspect each MIDI against the video
- [ ] Record findings and pick a default model in `docs/research/bakeoff.md`

### 3. Evaluation setup
- [ ] Get ground truth into MusicXML/MIDI (convert PDFs if needed)
- [ ] Synthetic covers: render pop-piano MIDI (e.g. POP909, verify contents) with piano sound libraries + reverb/noise/compression
- [ ] Classical proxies: amateur YouTube recordings of a Chopin nocturne, a Beethoven movement, Liebesträume No. 3, with IMSLP scores
- [ ] Check ASAP dataset (MAESTRO performances aligned to scores) for notation-only tests
- [ ] Scoring scripts in `eval/`: note F1 (`mir_eval`) for transcription; MV2H / `musicdiff` for notation
- [ ] Manual checklist per output: missed/extra notes, rhythm, hand split, spelling, cleanup time in MuseScore

### 4. Notation stages on perfect MIDI
- [ ] Run PM2S on ground-truth MIDI (ASAP + pop MIDI) as the baseline
- [ ] Build `clean`, `rhythm`, `engrave`; improve on PM2S where it falls short
- [ ] Check PM2S handles pop rhythms (trained on classical)

### 5. Connect real transcription
- [ ] Feed model MIDI from step 2 into the notation stages
- [ ] Measure the quality drop vs. perfect MIDI (= transcription error)

### 6. CLI
- [ ] `ingest` with YouTube/Instagram URLs and `--start/--end`
- [ ] `unotate transcribe` wiring all stages; writes `.musicxml` + raw `.mid`; prints run summary
- [ ] Unit tests per stage on small MIDI files; snapshot tests on fixed inputs

### 7. Iterate
- [ ] Target the weakest stage per the evaluation (likely hand split and rubato)
- [ ] Track cleanup time on real target covers as the main success measure
