# Version: v1.2.1

import json
import threading
import time

from PySide6.QtWidgets import QApplication

from ui.tray import AssistantTray
from core.audio import record_audio
from core.stt import transcribe
from core.intent import detect_intent
from core.actions import execute
from core.notifier import notify
from core.tts import speak

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
        CONFIG["whisper_exe"],
        CONFIG["whisper_model"],
        "recordings/temp.wav"
    )

    print(
        f"WHISPER TEXT: [{text}]"
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

        shutdown_assistant()

        return

    notify(response)


def hotkey_callback():

    threading.Thread(
        target=run_voice_request,
        daemon=True
    ).start()


#
# Double-tap RIGHT CTRL
#

DOUBLE_TAP_WINDOW = 0.45

last_right_ctrl = 0


def right_ctrl_pressed(event):

    global last_right_ctrl

    now = time.time()

    if (
        now - last_right_ctrl
        <= DOUBLE_TAP_WINDOW
    ):

        last_right_ctrl = 0

        hotkey_callback()

    else:

        last_right_ctrl = now


keyboard.on_press_key(
    "right ctrl",
    right_ctrl_pressed
)


tray.show()

app.exec()