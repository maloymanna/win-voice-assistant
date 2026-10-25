# Version: v1.0.2

import subprocess
import datetime

from core.tts import speak


def execute(
    intent,
    piper_exe,
    piper_model
):

    name = intent["intent"]

    if name == "open_app":

        speak(
            piper_exe,
            piper_model,
            "Opening application"
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

        speak(
            piper_exe,
            piper_model,
            response
        )

        return response

    if name == "mute":

        speak(
            piper_exe,
            piper_model,
            "Volume muted"
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
        piper_exe,
        piper_model,
        "Unknown command"
    )

    return "Unknown command"