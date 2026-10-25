import subprocess
import tempfile

def speak(
    piper_exe,
    model,
    text
):
    subprocess.run(
        [
            piper_exe,
            "-m",
            model
        ],
        input=text,
        text=True
    )
