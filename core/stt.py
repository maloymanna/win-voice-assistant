# Version: v1.1.0

import subprocess


def transcribe(
    parakeet_exe,
    parakeet_model,
    parakeet_vad_model,
    wav_file
):

    result = subprocess.run(
        [
            parakeet_exe,
            "transcribe",
            "--model",
            parakeet_model,
            "--input",
            wav_file,
            "--vad",
            "--vad-model",
            parakeet_vad_model
        ],
        capture_output=True,
        text=True,
        encoding="utf-8"
    )

    return result.stdout.strip().lower()