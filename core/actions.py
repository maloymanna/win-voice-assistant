# Version: v1.0.4

import subprocess
import datetime

from core.tts import speak


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

    if name == "time":

        now = datetime.datetime.now()

        response = now.strftime(
            "Current time is %H:%M"
        )

        return response

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