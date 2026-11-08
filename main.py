# Version: v1.6.0

import json
import subprocess
import threading
import time
import wave

import numpy as np
import sounddevice as sd
from PySide6.QtWidgets import QApplication

from ui.tray import AssistantTray
from core.audio import record_audio
from core.stt import transcribe
from core.intent import detect_intent
from core.actions import execute
from core.notifier import notify
from core.tts import speak, play_ding, speak_text

import keyboard


with open(
    "config/config.json",
    "r",
    encoding="utf-8"
) as f:

    CONFIG = json.load(f)


MODE = CONFIG.get("mode", "command")

SAMPLE_RATE = 16000
BLOCKSIZE = 512          # 32 ms at 16 kHz


app = QApplication([])

tray = AssistantTray(
    idle_icon="assets/tray_idle.ico",
    listening_icon="assets/tray_listening.ico"
)

tray.exit_requested.connect(
    lambda: shutdown_assistant()
)


# ------------------------------------------------------- stt-mode state

_stt_lock = threading.Lock()
_stt_recording = False
_stt_chunks = []
_stt_stream = None
_stt_safety_timer = None


def _stt_audio_callback(indata, frames, time_info, status):

    if _stt_recording:

        _stt_chunks.append(indata.copy())


def _stt_ensure_stream():

    global _stt_stream

    if _stt_stream is None:

        _stt_stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="int16",
            blocksize=BLOCKSIZE,
            callback=_stt_audio_callback
        )

        _stt_stream.start()

        print("STT: audio stream opened")


def _stt_safety_stop():

    print("STT: safety max duration reached")

    _stt_stop_and_transcribe()


def _stt_start():

    global _stt_recording, _stt_chunks, _stt_safety_timer

    try:

        _stt_ensure_stream()

    except Exception as e:

        print(f"STT: microphone unavailable: {e}")

        play_ding("negative_ding")

        notify(f"Microphone unavailable: {e}")

        tray.set_idle()

        return

    with _stt_lock:

        _stt_chunks = []

        _stt_recording = True

        max_sec = CONFIG.get(
            "record_seconds_stt_max", 120
        )

        _stt_safety_timer = threading.Timer(
            max_sec,
            _stt_safety_stop
        )

        _stt_safety_timer.daemon = True

        _stt_safety_timer.start()

    print("STT: recording started")


def _stt_stop_and_transcribe():

    global _stt_recording, _stt_chunks, _stt_safety_timer

    with _stt_lock:

        if not _stt_recording:

            return

        _stt_recording = False

        chunks = _stt_chunks

        _stt_chunks = []

        if _stt_safety_timer is not None:

            _stt_safety_timer.cancel()

            _stt_safety_timer = None

    tray.set_idle()

    if not chunks:

        print("STT: no audio captured")

        play_ding("negative_ding")

        notify("No speech detected")

        return

    audio = np.concatenate(chunks, axis=0)

    duration = len(audio) / SAMPLE_RATE

    print(
        f"STT: recording stopped ({duration:.1f}s)"
    )

    wav_path = "recordings/temp_stt.wav"

    with wave.open(wav_path, "wb") as wf:

        wf.setnchannels(1)

        wf.setsampwidth(2)

        wf.setframerate(SAMPLE_RATE)

        wf.writeframes(audio.tobytes())

    try:

        text = transcribe(CONFIG, wav_path)

    except Exception as e:

        print(f"STT: transcribe failed: {e}")

        play_ding("negative_ding")

        notify(f"Transcription failed: {e}")

        return

    print(f"STT TEXT: [{text}]")

    if not text.strip():

        play_ding("negative_ding")

        notify("No speech detected")

        return

    try:

        subprocess.run(
            ["clip"],
            input=text,
            text=True,
            shell=False,
            creationflags=subprocess.CREATE_NO_WINDOW,
            check=True
        )

    except Exception as e:

        print(f"STT: clipboard write failed: {e}")

        play_ding("negative_ding")

        notify(f"Clipboard failed: {e}")

        return

    play_ding("positive_ding")

    notify(text)


# ------------------------------------------------------- command mode flow

def run_voice_request():

    print("\n========== NEW REQUEST ==========")

    try:

        tray.set_listening()

        notify("Listening")

        speak(
            "assets/listening.wav"
        )

        record_audio(
            "recordings/temp.wav",
            CONFIG["record_seconds"]
        )

    finally:

        tray.set_idle()

    text = transcribe(
        CONFIG,
        "recordings/temp.wav"
    )

    print(
        f"STT TEXT: [{text}]"
    )

    intent = detect_intent(
        text
    )

    print(
        f"INTENT OBJECT: {intent}"
    )

    response = execute(
        intent
    )

    print(
        f"RESPONSE: {response}"
    )

    if response == "__EXIT__":

        speak(
            "assets/exiting_assistant.wav"
        )

        shutdown_assistant()

        return

    if CONFIG.get("speak_responses", False):

        speak_text(response)

    notify(response)


# ------------------------------------------------------- lifecycle

def shutdown_assistant():

    print("SHUTDOWN REQUESTED")

    global _stt_stream

    if _stt_stream is not None:

        try:
            _stt_stream.stop()
            _stt_stream.close()
        except Exception:
            pass

        _stt_stream = None

    tray.tray.hide()

    app.quit()


# ------------------------------------------------------- hotkey

DOUBLE_TAP_WINDOW = 0.45

last_right_ctrl = 0


def right_ctrl_pressed(event):

    global last_right_ctrl

    now = time.time()

    if now - last_right_ctrl > DOUBLE_TAP_WINDOW:

        last_right_ctrl = now

        return

    last_right_ctrl = 0

    if MODE == "stt":

        with _stt_lock:

            is_recording = _stt_recording

        if is_recording:

            threading.Thread(
                target=_stt_stop_and_transcribe,
                daemon=True
            ).start()

        else:

            tray.set_listening()

            notify("Listening")

            try:
                speak("assets/listening.wav")
            except Exception as e:
                print(f"LISTENING CUE FAILED: {e}")

            _stt_start()

        return

    threading.Thread(
        target=run_voice_request,
        daemon=True
    ).start()


keyboard.on_press_key(
    "right ctrl",
    right_ctrl_pressed
)


tray.show()

app.exec()