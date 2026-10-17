# Piano Transcription Models

Last checked: 2026-10-01 (web search).

## Key point

Most models train on **MAESTRO** (~200h of virtuoso competition performances on Yamaha Disklaviers, Liszt-heavy). Hard repertoire like Liebesträume is in-domain.

What actually breaks transcription:

1. **Recording mismatch**: phone mics, other pianos, room echo, compressed audio. A 2025 study ([arXiv 2512.14602](https://arxiv.org/abs/2512.14602)) measured a ~20-point note F1 drop from sound alone and ~14 from non-classical genre.
2. **Sustain pedal / note endings**: heavily pedalled arpeggios.
3. **MIDI ≠ sheet music**: quantizing to the beat, hand/voice separation, rubato, cadenza tuplets. This is the least solved step.

## Audio → MIDI

| Model | Year | MAESTRO F1 (approx.) | Pedal | Notes |
|---|---|---|---|---|
| Onsets and Frames (Magenta) | 2018 | ~95 | No | Classic baseline |
| High-Res Piano Transcription (Kong, ByteDance) | 2020 | ~96.7 | Yes | `piano_transcription_inference`, reliable |
| Seq2seq Transformer / MT3 (Google) | 2021 | ~96 | No | MT3 is multi-instrument; YourMT3+ (2024) improves on it |
| Transkun (Yan & Duan) | 2021, v2 2024 | ~97 | Yes | `pip install transkun` (v2.0.1). v2 checkpoint trained with augmentation; doesn't extend notes by pedal |
| hFT-Transformer (Sony) | 2023 | ~97.4 | No | Among the most accurate, heavier |
| Onsets & Velocities (Fernández) | 2023 | ~96.8 | No | Lightweight, near real-time |
| Edwards, Dixon & Benetos | 2024 | comparable | – | Augmentation-trained; better on real-world recordings |
| Basic Pitch (Spotify) | 2022 | lower | No | Tiny, browser-friendly, weak on dense piano |
| Streaming transcription (Wei, Yoshii et al.) | 2024 | ~offline SOTA | Yes | Real-time, separate onset/offset decoders |
| Efficient Transformer (Wei & Yoshii) | 2025 | ~baseline | – | Cheaper attention for whole-piece context; code on GitHub |
| **Aria-AMT** (EleutherAI) | 2025 | not published | – | Seq2seq, built for diverse pianos/recording quality. Used to transcribe ~100k hours (Aria-MIDI dataset). Weights on Hugging Face |

F1 numbers aren't strictly comparable across papers. Top models are within ~1 point; robustness to real recordings matters more.

## MIDI / Audio → Score

- **PM2S** (Liu et al., 2022): beat tracking, quantization, hand separation, key/time signature
- **Beyer & Dai** (2024): Transformer, performance MIDI → score end to end
- **End-to-end audio → score** (Zeng et al., 2024): bar- and note-level decoding, includes key/time signature; aimed at real-world audio. Research-grade
- **Joint transcription + rendering** (Zeng et al., ICLR 2026): separates score content from performance style. Research-grade
- **Penner & Hindle** (2026): full pipeline audio → Kong → hand/finger annotation → PM2S → MusicXML. ~91% hand-separation accuracy; code on Zenodo. Close to what unotate needs
- **Commercial to compare against:** Klangio Piano2Notes, AnthemScore, ScoreCloud

## By difficulty

- **Beginner:** any model works; score layout is the only real problem
- **Intermediate:** Kong or Transkun; pedal starts to matter
- **Liebesträume-level:** Transkun or hFT; score step is the bottleneck
- **Obscure repertoire:** fine if standard piano writing; risky for extended techniques, prepared piano, extreme registers

## Starting point

Transkun (or Kong) for audio → MIDI, PM2S for MIDI → score. Also try Aria-AMT on real phone recordings, since robustness matters most. Look at the Penner & Hindle pipeline as a reference.
