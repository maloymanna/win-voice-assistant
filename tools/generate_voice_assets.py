# Version: v1.6.0

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

    "assets/command_executed.wav":
        "Command executed",

    "assets/workflow_completed.wav":
        "Workflow completed",

    "assets/unknown_command.wav":
        "Unknown command",

    "assets/exiting_assistant.wav":
        "Exiting assistant",

    "assets/screenshot_saved.wav":
        "Screenshot saved",
}


Path("assets").mkdir(
    parents=True,
    exist_ok=True
)


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


def _generate_two_note(path, notes, sample_rate=22050,
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


def _generate_camera_shutter(path, sample_rate=22050,
                             duration=0.15, amplitude=0.4):

    n = int(sample_rate * duration)

    rng = np.random.default_rng(seed=42)

    noise = rng.standard_normal(n) * amplitude

    # Fast decay envelope: sharp click burst
    env = np.exp(-np.linspace(0, 8, n))

    wave = noise * env

    sf.write(
        path,
        wave,
        sample_rate,
        subtype="PCM_16"
    )


_generate_two_note(
    "assets/positive_ding.wav",
    [(880, 0.08), (1320, 0.12)]
)

print("Created: assets/positive_ding.wav")


_generate_two_note(
    "assets/negative_ding.wav",
    [(440, 0.12), (330, 0.18)]
)

print("Created: assets/negative_ding.wav")


_generate_two_note(
    "assets/close_or_exit.wav",
    [(523, 0.10), (392, 0.16)]
)

print("Created: assets/close_or_exit.wav")


_generate_camera_shutter(
    "assets/camera_shutter.wav"
)

print("Created: assets/camera_shutter.wav")


print("Done.")