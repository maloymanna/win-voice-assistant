# Version: v1.4.0

import json
import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf


with open(
    "config/config.json",
    "r",
    encoding="utf-8"
) as f:
    CONFIG = json.load(f)


SPOKEN_OUTPUTS = {
    "assets/listening.wav":
        "Listening",

    "assets/exiting_assistant.wav":
        "Exiting assistant",
}


Path("assets").mkdir(
    parents=True,
    exist_ok=True
)


# ---- spoken assets via Piper ----

for output_file, text in SPOKEN_OUTPUTS.items():

    subprocess.run(
        [
            CONFIG["piper_exe"],
            "-m",
            CONFIG["piper_model"],
            "-f",
            output_file
        ],
        input=text,
        text=True,
        check=True
    )

    print(f"Created: {output_file}")


# ---- ding assets, programmatically generated ----

def _generate_ding(path, notes, sample_rate=22050,
                   amplitude=0.5, fade_ms=5):

    fade_n = int(sample_rate * fade_ms / 1000)

    samples = []

    for freq, dur in notes:

        n = int(sample_rate * dur)

        t = np.linspace(0, dur, n, endpoint=False)

        wave = amplitude * np.sin(2 * np.pi * freq * t)

        if fade_n < n // 2:

            wave[:fade_n] *= np.linspace(0, 1, fade_n)

            wave[-fade_n:] *= np.linspace(1, 0, fade_n)

        samples.append(wave)

    sf.write(
        path,
        np.concatenate(samples),
        sample_rate,
        subtype="PCM_16"
    )


DINGS = {
    # ascending two-note chime: success
    "assets/positive_ding.wav": [
        (880, 0.08),
        (1320, 0.12)
    ],

    # descending two-note chime: error
    "assets/negative_ding.wav": [
        (440, 0.12),
        (330, 0.18)
    ],
}


for output_file, notes in DINGS.items():

    _generate_ding(output_file, notes)

    print(f"Created: {output_file}")


print("Done.")