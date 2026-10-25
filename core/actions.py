# Version: v1.0.6

import subprocess
import datetime
import tempfile

import sounddevice as sd
import soundfile as sf


def _speak_dynamic_time(time_text):

    with open(
        "config/config.json",
        "r",
        encoding="utf-8"
    ) as f:

        import json

        config = json.load(f)

    with tempfile.NamedTemporaryFile(
        suffix=".wav",
        delete=False
    ) as wavfile:

        wav_path = wavfile.name

    subprocess.run(
        [
            config["piper_exe"],
            "-m",
            config["piper_model"],
            "-f",
            wav_path
        ],
        input=time_text,
        text=True,
        check=True
    )

    data, samplerate = sf.read(
        wav_path
    )

    sd.play(
        data,
        samplerate
    )

    sd.wait()


def execute(intent):

    name = intent["intent"]

    if name == "open_app":

        from core.tts import speak

        speak(
            "assets/opening_application.wav"
        )

        subprocess.Popen(
            intent["target"]
        )

        return "Opening application"

    if name == "time":

        now = datetime.datetime.now()

        time_text = now.strftime(
            "%I %M %p"
        ).lstrip("0")

        _speak_dynamic_time(
            f"The current time is {time_text}"
        )

        return (
            f"Current time is {time_text}"
        )

    if name == "mute":

        from core.tts import speak

        speak(
            "assets/volume_muted.wav"
        )

        subprocess.run(
            [
                "powershell",
                "-Command",
                "(New-Object -ComObject WScript.Shell).SendKeys([char]173)"
            ]
        )

        return "Volume muted"

    from core.tts import speak

    speak(
        "assets/unknown_command.wav"
    )

    return "Unknown command"