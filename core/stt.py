# Version: v1.0

import subprocess


def transcribe(
    whisper_exe,
    model,
    wav_file
):

    result = subprocess.run(
        [
            whisper_exe,
            "-m",
            model,
            "-f",
            wav_file
        ],
        capture_output=True,
        text=True,
        encoding="utf-8"
    )

    return result.stdout.strip().lower()