# Version: v1.0.2

import json

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from ui.tray import AssistantTray

from core.audio import record_audio
from core.stt import transcribe
from core.tts import speak
from core.intent import detect_intent
from core.actions import execute
from core.notifier import notify


with open(
    "config/config.json",
    "r",
    encoding="utf-8"
) as f:
    CONFIG = json.load(f)


VOICE_MAP = {
    "Listening": "assets/listening.wav",
    "Opening application": "assets/opening_application.wav",
    "Unknown command": "assets/unknown_command.wav"
}


def listen():

    speak(
        CONFIG["piper_exe"],
        CONFIG["piper_model"],
        "Listening"
    )

    notify("Listening")

    record_audio(
        "recordings/temp.wav",
        CONFIG["record_seconds"]
    )

    text = transcribe(
        CONFIG["whisper_exe"],
        CONFIG["whisper_model"],
        "recordings/temp.wav"
    )

    intent = detect_intent(text)

    response = execute(
        intent,
        CONFIG["piper_exe"],
        CONFIG["piper_model"]
    )

    notify(response)


app = QApplication([])

tray = AssistantTray(
    QIcon("assets/icon_idle.ico"),
    listen
)

tray.show()

app.exec()