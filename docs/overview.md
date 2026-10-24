## Overview
Converts piano music from a YouTube video URL into a sheet music downloadable. This could later be edited by the user through external software like MuseScore depending on how content they are with the transcription.

## Architecture

CLI. This project will run locally. Run one command to convert the audio.

Backend
- language: python? may need to run some AI models

## Usage

CLI: `unotate transcribe <url-or-file> -o out.musicxml`


## Scope:
- Only for personal use
- Only meant for piano
    - No background instrumental
    - No other instrument + piano
- Input: youtube URL, mp3 file
    - average cases:   
        - single piano piece
            - examples: liszt liebestraume no. 3, any chopin nocturne, beethoven sonata
- Output: not sure
    - More universal file like a .musicxml
    - alternatively, musescore file

