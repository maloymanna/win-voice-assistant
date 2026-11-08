# Version: v1.2.0

import json
import os
import subprocess
import tempfile

import sounddevice as sd
import soundfile as sf


def speak(wav_file):

    data, samplerate = sf.read(
        wav_file
    )

    sd.play(
        data,
        samplerate
    )

    sd.wait()


def play_ding(name):

    path = f"assets/{name}.wav"

    try:

        speak(path)

    except Exception as e:

        print(
            f"DING PLAY FAILED: {path} ({e})"
        )


def speak_text(text):

    if not text or not str(text).strip():
        return

    with open(
        "config/config.json",
        "r",
        encoding="utf-8"
    ) as f:

        config = json.load(f)

    fd, wav_path = tempfile.mkstemp(
        suffix=".wav"
    )

    os.close(fd)

    try:

        subprocess.run(
            [
                config["piper_exe"],
                "-m",
                config["piper_model"],
                "-f",
                wav_path
            ],
            input=str(text),
            text=True,
            check=True
        )

        speak(wav_path)

    finally:

        try:
            os.remove(wav_path)
        except OSError:
            pass