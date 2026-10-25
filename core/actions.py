# Version: v1.0.8

import subprocess
import datetime
import tempfile
import json

import sounddevice as sd
import soundfile as sf

from core.tts import speak


def _speak_dynamic_time(time_text):

    with open(
        "config/config.json",
        "r",
        encoding="utf-8"
    ) as f:

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

        speak(
            "assets/opening_application.wav"
        )

        subprocess.Popen(
            intent["target"]
        )

        return "Opening application"

    if name == "open_url":

        speak(
            "assets/opening_application.wav"
        )

        subprocess.Popen(
            [
                "msedge.exe",
                "--new-tab",
                intent["target"]
            ]
        )

        return "Opening website"

    if name == "workflow":

        speak(
            "assets/opening_application.wav"
        )

        for step in intent["steps"]:

            if step["intent"] == "open_url":

                subprocess.Popen(
                    [
                        "msedge.exe",
                        "--new-tab",
                        step["target"]
                    ]
                )

            elif step["intent"] == "open_app":

                subprocess.Popen(
                    step["target"]
                )

        return "Workflow completed"

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

    speak(
        "assets/unknown_command.wav"
    )

    return "Unknown command"