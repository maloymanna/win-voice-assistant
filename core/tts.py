# Version: v1.0

import subprocess
import tempfile

import sounddevice as sd
import soundfile as sf


def speak(
    piper_exe,
    model,
    text
):

    with tempfile.NamedTemporaryFile(
        suffix=".wav",
        delete=False
    ) as wavfile:

        wav_path = wavfile.name

    subprocess.run(
        [
            piper_exe,
            "-m",
            model,
            "-f",
            wav_path
        ],
        input=text,
        text=True,
        check=True
    )

    data, samplerate = sf.read(wav_path)

    sd.play(data, samplerate)
    sd.wait()