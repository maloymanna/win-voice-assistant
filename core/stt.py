import subprocess
import json

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
            wav_file,
            "-oj"
        ],
        capture_output=True,
        text=True
    )

    data = json.loads(result.stdout)

    return data["transcription"].strip().lower()
