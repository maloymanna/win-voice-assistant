# Version: v1.0

import subprocess
import datetime


def execute(intent):

    name = intent["intent"]

    if name == "open_app":

        subprocess.Popen(
            intent["target"]
        )

        return "Opening application"

    if name == "time":

        now = datetime.datetime.now()

        return now.strftime(
            "Current time is %H:%M"
        )

    if name == "mute":

        subprocess.run(
            [
                "powershell",
                "-Command",
                "(New-Object -ComObject WScript.Shell).SendKeys([char]173)"
            ]
        )

        return "Volume muted"

    return "Unknown command"