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
- each file is opened in Windows Media Player and ran
- visual/auditory inspection to original video or sheets (if provided in video)

## Initial Results

### Musescore
- Mostly all the notes are accounted for across both models
- Kong accounts for pedal, while Transkun doesn't. This results in Kong having an extremely high amount of tied notes, making the sheets messy (giving the sheets a "that just looks wrong" quality from the perspective of someone who regularly reads music). 
- Both create weird rhythms (like a 32nd note) to attempt to match the exact notes in audio. Notes like grace notes are handled poorly: instead, very short notes or layed notes are written.
- Transkun generally results in a cleaner sheet. 

### Windows Media Player
- Transkun: from ear, it sounds very close to the original audio
    - djjediforce, fairy tale: some issues. might have uncessary octave notes
    - call of silence: good
    - love: clean
    - if im with you: clean
    - huge, hampstead: clean
- Kong: mostly correct, sometimes it sounds like extra chord notes are being added
    - djjediforce, fairy tale: 
        - first 10 measures you can really hear octaves when there should be a single note
        - chorus has extra notes (like the jittering/shaking effect of hand). very messy notes in latter half of chorus
    - call of silence: correct notes but extremely messy addition of extra notes
    - love: very messy
    - if im with you: octaves and extra notes in chords
    - hugo, hampstead: clean, except repeated notes (like playing two quarter notes instead of one half note of the same pitch)

In general, Transkun performs better. Upon aural evaluation, Transkun will be selected as the default model.

### Thoughts

- MIDI audio outputs seem good for this stage. Converting those to Musescore and looking at the sheet music is not fine for the most part (cleanable but will likely require a good amount of work). The next stage should be MIDI to 
- if the primary purpose is a tool that converts audio to sheets, using a tool like Transkun may be all that's needed, ASSUMING that human intervention will be needed anyway to clean up the sheets. the hard part of going from audio --> sheets (manually) is the first stage of putting most of the notes on the page. I'd expect that once the foundation is laid out, cleaning up will be much quicker.
- other projects/pivots to consider:
    - computer vision to write notes/sheets based on an overhead view of piano keys (think BELLA&LUCAS videos)
        - more conditional logic involved (if this key is pressed down, it's being played)
    - PDF/image to .musicxml/.mscz file
        - addresses the problem of buying sheet music and then having to transcribe it all over again if any custom edits need to be made to it (transpose, add instrument, edit notes, etc.)