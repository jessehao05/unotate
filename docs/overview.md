## Overview
Converts piano music from a YouTube video URL into a sheet music downloadable. This could later be edited by the user through external software like MuseScore depending on how content they are with the transcription.

## Architecture

Deployment requirements: needs to be free. Ideally would have an easy public URL (not too long).

Frontend:
- deployment on vercel, so whatever fits well
    - language: TypeScript
    - framework: react + vite vs. nextjs

Backend
- language: python? may need to run some AI models
- framework: fastapi
- deployment on render? 

Note: deployment may not be necessary. I'm fine with running locally, but ideally the process would be more streamlined than: cd frontend, run frontend, cd backend, run backend. If there was one way to run the whole project from the terminal or something else, that would be great.


## Scope:
- Only for personal use
- Only meant for piano
    - No background instrumental
    - No other instrument + piano
- Input: youtube URL, mp3 file
    - average cases:   
        - single piano piece
            - examples: liszt liebestraume no. 3, any chopin nocturne, beethoven sonata
        - piano 4 hands duet
            - examples: BELLA&LUCAS arrangement
- Output: not sure
    - for piano duets: I'm not expecting the model to separate which hands play which notes, since this is impossible. I simply want all the notes that were played, and a human in the loop can manually finish the task.
    - PNG? Not idea for post processing
    - Musescore file? Probably best
    - More universal file like a 

