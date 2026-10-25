# Version: v1.0.4

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