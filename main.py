# Version: v1.2.0

import json
import threading

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from ui.tray import AssistantTray
from core.audio import record_audio
from core.stt import transcribe
from core.tts import speak
from core.intent import detect_intent
from core.actions import execute
from core.notifier import notify

import keyboard


with open(
    "config/config.json",
    "r",
    encoding="utf-8"
) as f:

    CONFIG = json.load(f)


app = QApplication([])

tray = AssistantTray(
    idle_icon="assets/tray_idle.ico",
    listening_icon="assets/tray_listening.ico"
)


def shutdown_assistant():

    print("SHUTDOWN REQUESTED")

    tray.tray.hide()

    app.quit()


def run_voice_request():

    print("\n========== NEW REQUEST ==========")

    try:

        tray.set_listening()

        speak("assets/listening.wav")

        notify("Listening")

        record_audio(
            "recordings/temp.wav",
            CONFIG["record_seconds"]
        )

    finally:

        tray.set_idle()

    text = transcribe(
        CONFIG["whisper_exe"],
        CONFIG["whisper_model"],
        "recordings/temp.wav"
    )

    print(f"WHISPER TEXT: [{text}]")

    intent = detect_intent(text)

    print(f"INTENT OBJECT: {intent}")

    response = execute(intent)

    print(f"RESPONSE: {response}")

    if response == "__EXIT__":

        shutdown_assistant()
        return

    notify(response)


def hotkey_callback():

    threading.Thread(
        target=run_voice_request,
        daemon=True
    ).start()


keyboard.add_hotkey(
    "windows+q",
    hotkey_callback
)

tray.show()

app.exec()