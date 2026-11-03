# Version: v1.2.0

import subprocess


def _transcribe_parakeet(
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


def _transcribe_whisper(
    whisper_exe,
    whisper_model,
    wav_file
):

    result = subprocess.run(
        [
            whisper_exe,
            "-m",
            whisper_model,
            "-f",
            wav_file
        ],
        capture_output=True,
        text=True,
        encoding="utf-8"
    )

    return result.stdout.strip().lower()


def transcribe(config, wav_file):

    engine = config.get("stt_engine", "parakeet")

    if engine == "parakeet":

        return _transcribe_parakeet(
            config["parakeet_exe"],
            config["parakeet_model"],
            config["parakeet_vad_model"],
            wav_file
        )

    if engine == "whisper":

        return _transcribe_whisper(
            config["whisper_exe"],
            config["whisper_model"],
            wav_file
        )

    raise ValueError(
        f"Unknown stt_engine: {engine}"
    )