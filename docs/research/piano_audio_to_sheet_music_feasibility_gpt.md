# Piano Audio → Sheet Music Transcription Project
## Feasibility Analysis & Development Plan

> **Purpose:** Preserve the feasibility analysis of this project so it can be revisited later.

---

## 1. Project Overview

The proposed project converts piano music from a YouTube video URL or an audio file into downloadable sheet music. The intended workflow allows the resulting transcription to be edited manually in external software such as MuseScore.

The current scope is intentionally narrow:

- Personal use
- Piano only
- No background instrumentation
- No piano + another instrument
- Input: YouTube URL or MP3
- Target examples: solo piano pieces such as Liszt's *Liebestraum No. 3*, Chopin nocturnes, Beethoven sonatas, and four-hand piano arrangements
- For piano duets, there is no expectation that the system will determine which performer/hand played each note.
- Human cleanup/editing is explicitly part of the workflow.

## 2. Overall Feasibility

### Verdict

**The project is very feasible as a personal project.**

The important distinction is:

> Building a pipeline that turns piano audio into editable MIDI/MusicXML is feasible. Building one that automatically produces polished, publication-quality sheet music is substantially harder.

| Component | Feasibility | Difficulty |
|---|---|---|
| MP3 → piano notes | Very feasible | Medium |
| YouTube URL → audio | Feasible | Low–Medium |
| Polyphonic piano transcription | Feasible | Medium–High |
| Piano duet transcription | Feasible with limitations | High |
| Notes → MIDI | Very feasible | Low |
| MIDI → MusicXML | Very feasible | Low–Medium |
| MusicXML → MuseScore | Very feasible | Low |
| Automatically produce beautiful sheet music | Possible, but difficult | High |
| Free public deployment | Technically possible, but awkward | High |
| Fully local application | Very feasible | Low |

Overall: approximately **8/10 feasible** for the stated personal-use goal.

---

## 3. The Core AI Problem Is Already Largely Solved

The project does **not** need to start by training an original AI model.

Existing automatic music transcription (AMT) models can already convert audio into note information/MIDI.

Potential starting points include:

### Spotify Basic Pitch

Basic Pitch accepts audio and produces MIDI. It supports polyphonic instruments and is particularly appropriate when working with one instrument at a time.

Repository:
https://github.com/spotify/basic-pitch

### Magenta Onsets and Frames

Onsets and Frames is specifically designed for piano transcription.

Repository:
https://github.com/magenta/magenta/tree/main/magenta/models/onsets_frames_transcription

### Magenta MT3

MT3 is a more general automatic music transcription system with a piano transcription model/checkpoint.

Repository:
https://github.com/magenta/mt3

### Implication

The project is better framed as:

> **Build a useful application around existing piano transcription models.**

rather than:

> Build an AI system that understands piano from scratch.

---

## 4. Proposed Core Pipeline

```text
YouTube URL / MP3
        ↓
    Audio extraction
        ↓
   Audio preprocessing
        ↓
 Piano transcription model
        ↓
       MIDI
        ↓
  MIDI post-processing
        ↓
    MusicXML
        ↓
     Download
        ↓
     MuseScore
```

A concrete implementation could look like:

```text
audio
  ↓
Basic Pitch / Onsets & Frames / MT3
  ↓
MIDI
  ↓
pretty_midi / music21
  ↓
MusicXML
  ↓
MuseScore
```

The key architectural decision is to use **MIDI as the intermediate representation** rather than trying to directly generate sheet music from audio.

---

## 5. Why MIDI Should Be an Intermediate Representation

The intuition that PNG is not a good output format is correct.

### MIDI

Pros:
- Easy to generate
- Excellent intermediate representation
- MuseScore can open it
- Easy to manipulate programmatically

Cons:
- Does not preserve all notation information
- Does not inherently represent polished engraving

### MusicXML

Pros:
- Designed for sheet music interchange
- Supported by MuseScore
- Portable between notation applications
- Can represent measures, notes, rests, clefs, time signatures, etc.

Cons:
- More complicated to generate correctly

### MuseScore `.mscz`

Pros:
- Native MuseScore format

Cons:
- Couples the project more closely to MuseScore
- Harder to generate correctly
- Less universal

### Recommendation

Use:

```text
Audio
 ↓
MIDI
 ↓
MusicXML
 ↓
MuseScore
```

Make **MusicXML the primary sheet-music output**, with MIDI as an additional downloadable output.

---

## 6. The Hardest Part Isn't Detecting Notes

The most important technical distinction is between:

> detecting what notes were played

and:

> producing polished sheet music.

A transcription model can potentially determine:
- Which pitches were played
- Approximately when they started
- Approximately when they ended
- Potentially velocity/dynamics information

But sheet music requires musical interpretation, including:
- Measures
- Time signatures
- Rests
- Voices
- Beaming
- Ties
- Tuplets
- Accidentals
- Clefs
- Pedal markings
- Hand/staff assignment
- Enharmonic spelling
- Note grouping

Therefore the project's realistic goal should be:

> **Audio → reasonably accurate MIDI → usable MusicXML**

rather than:

> Audio → perfect sheet music.

---

## 7. Human-in-the-Loop Is a Major Strength

The decision to allow manual cleanup is very sensible.

A reasonable workflow is:

```text
YouTube
   ↓
automatic transcription
   ↓
MIDI
   ↓
MusicXML
   ↓
open in MuseScore
   ↓
human cleanup
```

The system does not have to replace a professional music transcriber. It needs to get the user most of the way there.

This philosophy can apply to the entire project:

> **Aim for a useful first-pass transcription that a human can correct.**

---

## 8. Solo Piano Should Be the First Target

Keep the current restrictions for the initial version:

- Solo piano
- No background instrumental
- No other instrument + piano

This makes the problem much more manageable.

A recording such as a solo Chopin nocturne is fundamentally easier than piano + orchestra + vocals + drums.

The narrower input scope is therefore a significant advantage.

---

## 9. Piano Duets

Four-hand piano is possible, but there is an important limitation.

A recording gives the model a combined audio signal:

```text
Person A             Person B
   ↓                    ↓
      └──── piano ──────┘
               ↓
        single audio signal
```

The transcription model does not inherently know which performer or hand played every note.

However, that does not need to be solved for the MVP.

The system could produce a combined piano transcription and let the user reorganize it afterward.

---

## 10. Deployment: Local First

The original plan considers:
- React/Vite or Next.js frontend
- TypeScript
- FastAPI backend
- Render
- Vercel
- Free deployment
- Easy public URL

That architecture is possible, but it should **not** be the starting point.

For personal use, local execution is attractive because transcription can be computationally expensive.

The local architecture could initially be:

```text
Your computer
       ↓
     Python
       ↓
     GPU
       ↓
    MIDI/XML
```

The user's RTX 4060 Laptop GPU and 32 GB RAM make local experimentation practical.

Local execution avoids:
- Model hosting
- GPU availability
- Inference costs
- Request timeouts
- Large audio uploads
- Backend cold starts
- Temporary file storage
- Free-tier limitations

The public/free deployment requirement should therefore be treated as a **later feature**, not an MVP requirement.

---

## 11. Recommended Initial Architecture

For the first version, skip the full web stack.

Start with:

```text
piano-transcriber/
├── transcription/
├── audio/
├── midi/
├── musicxml/
└── main.py
```

Then make it executable with:

```bash
python main.py input.mp3
```

The program would:
1. Accept an MP3/WAV
2. Preprocess audio if necessary
3. Run the transcription model
4. Produce MIDI
5. Optionally convert MIDI to MusicXML
6. Save the output files

Only after that works should the web application be added.

---

## 12. Development Progression

### MVP 1 — MP3 → MIDI

Start with:

```text
MP3/WAV
   ↓
transcription model
   ↓
MIDI
```

Example:

```bash
python transcribe.py song.mp3
```

Output:

```text
song.mid
```

No YouTube, React, FastAPI, deployment, or MusicXML yet.

If this works on real piano pieces, the hardest core assumption has been validated.

### MVP 2 — MIDI → MusicXML

Add:

```text
MIDI
 ↓
MusicXML
```

Then:

```text
song.mp3
    ↓
song.mid
    ↓
song.musicxml
```

Open the MusicXML in MuseScore and inspect the result.

### MVP 3 — YouTube Input

Add:

```text
YouTube URL
     ↓
download/extract audio
     ↓
transcription
     ↓
MIDI
     ↓
MusicXML
```

### MVP 4 — Web Frontend

Add:

```text
React/Vite
     ↓
FastAPI
     ↓
Python transcription pipeline
```

### MVP 5 — Deployment

Only after the local application works should free/public hosting be investigated.

---

## 13. Potential Technical Challenge: Music Notation Post-Processing

This is probably the area where the project could become more substantial than simply wrapping an existing AI model.

A raw transcription might conceptually look like:

```text
C4 at 0.001
E4 at 0.003
G4 at 0.005
C5 at 0.998
...
```

Post-processing could perform:

```text
raw transcription
       ↓
remove extremely short notes
       ↓
quantize timing
       ↓
estimate tempo
       ↓
detect beats
       ↓
infer measures
       ↓
assign notes to treble/bass
       ↓
generate MusicXML
```

This creates meaningful engineering/algorithmic work.

---

## 14. Potential Model Comparison

Instead of training a new model, the project could compare existing transcription systems:

```text
                 ┌─ Basic Pitch ─────┐
Audio ───────────┼─ Onsets & Frames ─┼──→ compare
                 └─ MT3 ─────────────┘
```

Potential comparison criteria:
- Note accuracy
- Timing accuracy
- False positive notes
- Missed notes
- Chord accuracy
- Performance on dense passages
- Performance on soft passages
- Performance on pedal-heavy passages
- Runtime
- GPU/CPU resource usage
- Quality of resulting MIDI/MusicXML

This gives the project a meaningful engineering/research component without requiring development of a neural network from scratch.

---

## 15. Potential Future UI Feature: Piano Roll

A useful future feature would be a piano-roll visualization:

```text
C6 ────────
B5      ───────
A5 ─────────────
G5       ────────
...
```

A future UI could show:

```text
Transcription complete

Duration:       4:37
Detected notes: 2,841
Estimated BPM:  72

[View Piano Roll]

[Download MIDI]
[Download MusicXML]
```

This would let the user inspect the transcription before worrying about notation.

---

## 16. Important Project Boundary

### Realistic goal

> Give me an audio recording of a solo piano performance and produce a MIDI/MusicXML transcription that is good enough for me to clean up in MuseScore.

### Much less realistic goal

> Give me any piano YouTube video and automatically produce professional-quality sheet music.

The current project scope is much closer to the first goal because it explicitly allows human cleanup.

---

## 17. Recommended Technical Stack

### Initial prototype

```text
Python
Existing AMT model
MIDI library
MusicXML/music-notation library
MuseScore for manual cleanup
```

### Later application

```text
Frontend:
TypeScript
React + Vite

Backend:
Python
FastAPI

Transcription:
Basic Pitch / Onsets & Frames / MT3

Output:
MIDI
MusicXML

Development:
Local GPU first

Deployment:
Investigate after local version works
```

There is no strong reason to choose Next.js over React/Vite at the beginning. Since the application is primarily a client UI over a Python backend, React + Vite is a straightforward fit.

---

## 18. Suggested Project Structure

```text
piano-transcriber/
│
├── backend/
│   ├── api/
│   ├── audio/
│   ├── transcription/
│   ├── midi/
│   ├── musicxml/
│   └── main.py
│
├── frontend/
│   └── ...
│
├── tests/
│
├── examples/
│
├── README.md
│
└── run.py
```

A single launcher could eventually handle the whole application:

```bash
python run.py
```

Docker Compose is another possible later solution.

---

## 19. Recommended First Experiments

Before building the frontend, test transcription quality on a small benchmark.

### Test set

1. Simple solo piano piece
2. Chopin nocturne
3. Beethoven sonata movement
4. Liszt piece
5. Dense/chord-heavy piece
6. Very soft piece
7. Fast piece
8. Four-hand arrangement

For each:

```text
Input audio
    ↓
Model
    ↓
MIDI
    ↓
Inspect MIDI
    ↓
Convert to MusicXML
    ↓
Open in MuseScore
    ↓
Evaluate manually
```

Track:
- Missed notes
- Extra notes
- Timing errors
- Chord errors
- Rhythm/quantization errors
- Notation problems
- Runtime

This will tell you much more about project feasibility than building the web UI first.

---

## 20. Bottom Line

**Yes — this is a reasonable project to build.**

The project is feasible because:
- The scope is constrained.
- Existing transcription models can handle the difficult audio-to-note component.
- Human cleanup is explicitly allowed.
- Local GPU execution is practical.
- MIDI and MusicXML provide a natural interchange pipeline.

The most sensible strategy is:

```text
1. MP3 → MIDI
2. MIDI → MusicXML
3. Test in MuseScore
4. Add YouTube input
5. Improve post-processing
6. Build FastAPI backend
7. Build React frontend
8. Consider deployment
```

The central design philosophy should be:

> **Automatic first-pass transcription + human cleanup**, not perfect automatic sheet music.

The part worth investing your own engineering effort into is the post-processing and notation pipeline:

```text
Audio
 ↓
Existing AI transcription
 ↓
Raw MIDI
 ↓
Your algorithms
 ↓
Clean/quantized musical representation
 ↓
MusicXML
 ↓
MuseScore
```

That keeps the project feasible while still leaving plenty of meaningful software/algorithmic work to build.
