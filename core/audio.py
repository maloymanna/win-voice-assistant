# Version: v1.0

import sounddevice as sd
import soundfile as sf
from pathlib import Path


def record_audio(output_path, seconds=5):

    Path(output_path).parent.mkdir(
        parents=True,
        exist_ok=True
    )

    samplerate = 16000

    audio = sd.rec(
        int(seconds * samplerate),
        samplerate=samplerate,
        channels=1,
        dtype="float32"
    )

    sd.wait()

    sf.write(
        str(Path(output_path).resolve()),
        audio,
        samplerate
    )