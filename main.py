# Version: v1.5.0

import json
import queue
import threading
import time

import numpy as np
import sounddevice as sd
from PySide6.QtWidgets import QApplication

from ui.tray import AssistantTray
from core.audio import record_audio
from core.stt import transcribe
from core.intent import detect_intent
from core.actions import execute
from core.notifier import notify
from core.tts import speak, speak_text
from core.streaming_vad import StreamingVAD

import keyboard


with open(
    "config/config.json",
    "r",
    encoding="utf-8"
) as f:

    CONFIG = json.load(f)


MODE = CONFIG.get("mode", "command")

SAMPLE_RATE = 16000
FRAME_SAMPLES = 512          # 32 ms at 16 kHz
FRAME_BYTES = FRAME_SAMPLES * 2   # int16


app = QApplication([])

tray = AssistantTray(
    idle_icon="assets/tray_idle.ico",
    listening_icon="assets/tray_listening.ico"
)

tray.exit_requested.connect(
    lambda: shutdown_assistant()
)


# ---------------------------------------------------------------- hotkey state

recording_active = False
stop_requested = False
_hotkey_lock = threading.Lock()


def request_stop():

    global stop_requested

    with _hotkey_lock:
        stop_requested = True


# ---------------------------------------------------------------- streaming stt

def _record_streaming_stt():

    """
    Returns a path to a WAV file with the captured audio.
    Uses streaming VAD to stop automatically on silence,
    or on hotkey toggle.
    """

    global recording_active, stop_requested

    vad = StreamingVAD(
        CONFIG.get("parakeet_lib", ""),
        CONFIG["parakeet_vad_model"]
    )

    vad.set_min_pause(
        CONFIG.get("vad_min_pause", 0.1)
    )

    max_seconds = CONFIG.get(
        "record_seconds_stt_max", 120
    )

    audio_queue = queue.Queue()

    def _callback(indata, frames, time_info, status):
        # Keep the callback light: copy and enqueue only.
        audio_queue.put(indata.copy())

    collected = []
    speech_started = False
    start_time = time.time()

    try:

        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="int16",
            blocksize=FRAME_SAMPLES,
            callback=_callback
        ):

            print("STREAMING STT: listening")

            while True:

                if stop_requested:
                    print("STREAMING STT: hotkey stop")
                    break

                if time.time() - start_time > max_seconds:
                    print("STREAMING STT: max duration reached")
                    break

                try:
                    chunk = audio_queue.get(timeout=0.1)
                except queue.Empty:
                    continue

                collected.append(chunk)

                started, ended = vad.feed(
                    chunk.tobytes()
                )

                if started:
                    speech_started = True

                if ended and speech_started:
                    print("STREAMING STT: silence stop")
                    break

    except Exception as e:

        print(f"STREAMING STT FAILED: {e}")
        return None

    finally:

        vad.close()

        with _hotkey_lock:
            recording_active = False
            stop_requested = False

    if not collected:
        return None

    audio = np.concatenate(collected, axis=0)

    # Write a minimal 16 kHz mono int16 WAV
    import wave

    path = "recordings/temp_stt.wav"

    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(audio.tobytes())

    return path


# ---------------------------------------------------------------- stt mode flow

def _run_stt_mode():

    global recording_active, stop_requested

    with _hotkey_lock:
        recording_active = True
        stop_requested = False

    try:

        tray.set_listening()
        notify("Listening")

        try:
            speak("assets/listening.wav")
        except Exception:
            pass

        wav_path = _record_streaming_stt()

    finally:

        tray.set_idle()

        with _hotkey_lock:
            recording_active = False
            stop_requested = False

    if not wav_path:
        notify("No speech detected")
        return

    text = transcribe(CONFIG, wav_path)

    print(f"STT TEXT: [{text}]")

    if text.strip():

        try:
            import subprocess
            subprocess.run(
                ["clip"],
                input=text,
                text=True,
                shell=False,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        except Exception as e:
            print(f"CLIPBOARD WRITE FAILED: {e}")

        notify(text)

    else:

        notify("No speech detected")


# ---------------------------------------------------------------- command mode

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


# ---------------------------------------------------------------- tray / exit

def shutdown_assistant():

    print("SHUTDOWN REQUESTED")

    tray.tray.hide()

    app.quit()


# ---------------------------------------------------------------- hotkey

DOUBLE_TAP_WINDOW = 0.45

last_right_ctrl = 0


def right_ctrl_pressed(event):

    global last_right_ctrl, recording_active

    now = time.time()

    if now - last_right_ctrl > DOUBLE_TAP_WINDOW:

        last_right_ctrl = now
        return

    last_right_ctrl = 0

    if MODE == "stt":

        with _hotkey_lock:

            if recording_active:
                request_stop()
                return

        threading.Thread(
            target=_run_stt_mode,
            daemon=True
        ).start()

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