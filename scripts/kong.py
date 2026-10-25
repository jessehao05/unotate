import sys
import types
from pathlib import Path

import librosa

# piano_transcription_inference imports matplotlib.pyplot but never uses it, and
# Smart App Control blocks matplotlib's ft2font DLL on the primary machine.
sys.modules["matplotlib"] = types.ModuleType("matplotlib")
sys.modules["matplotlib.pyplot"] = types.ModuleType("matplotlib.pyplot")
from piano_transcription_inference import PianoTranscription, sample_rate

transcriptor = PianoTranscription(device="cuda", checkpoint_path=None)
out = Path("data/out/kong")
out.mkdir(parents=True, exist_ok=True)
paths = [Path(p) for p in sys.argv[1:]] or sorted(Path("data/raw").glob("*.mp3"))
for path in paths:
    audio, _ = librosa.load(path, sr=sample_rate, mono=True)
    transcriptor.transcribe(audio, str(out / f"{path.stem}.mid"))
