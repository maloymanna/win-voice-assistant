# Version: v1.0.3

import json
import subprocess
from pathlib import Path


with open(
    "config/config.json",
    "r",
    encoding="utf-8"
) as f:
    CONFIG = json.load(f)


OUTPUTS = {
    "assets/listening.wav":
        "Listening",

    "assets/opening_application.wav":
        "Opening application",

    "assets/unknown_command.wav":
        "Unknown command",

    "assets/volume_muted.wav":
        "Volume muted"
}


Path("assets").mkdir(
    parents=True,
    exist_ok=True
)


for output_file, text in OUTPUTS.items():

    subprocess.run(
        [
            CONFIG["piper_exe"],
            "-m",
            CONFIG["piper_model"],
            "-f",
            output_file
        ],
        input=text,
        text=True,
        check=True
    )

    print(
        f"Created: {output_file}"
    )


print("Done.")