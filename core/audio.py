import sounddevice as sd
import soundfile as sf

def record_audio(output_path, seconds=5):
    samplerate = 16000

    audio = sd.rec(
        int(seconds * samplerate),
        samplerate=samplerate,
        channels=1
    )

    sd.wait()

    sf.write(
        output_path,
        audio,
        samplerate
    )
