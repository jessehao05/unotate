# Bakeoff Results: Transkun vs. Kong

## Data:
Songs tested:
- Hampstead, TutorialsByHugo (ground truth provided)
- Tong Hua, djjedforce (ground truth provided)
- Hampstead, Sing2Piano (same song, different arranger/piano)
- call of silence, gentle_motif (heavy reverb/pedal) (ground truth can be generated)
- if im with you, hanaisdao_ (ground truth can be generated)
- love, goanklm_

## Procedure

- run each song through both Transkun and Kong, converting it from .mp3 to .mid
- results are stored in `data/out/kong` or `data/out/transkun` (which are gitignored)
- each file is opened in Musescore and ran
- visual/auditory inspection to original video or sheets (if provided in video)

## Initial Results

- Pretty much all the notes are accounted for across both models
- Kong accounts for pedal, while Transkun doesn't. This results in Kong having an extremely high amount of tied notes, making the sheets messy (giving the sheets a "that just looks wrong" quality from the perspective of someone who regularly reads music). 
- Both create weird rhythms (like a 32nd note) to attempt to match the exact notes in audio. Notes like grace notes are handled poorly: instead, very short notes or layed notes are written.
- Transkun generally results in a cleaner sheet. 