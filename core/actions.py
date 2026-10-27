# core/actions.py
# Version: v1.3.0

import subprocess
import datetime
import tempfile
import json
import yaml

import sounddevice as sd
import soundfile as sf

from core.tts import speak


def _load_yaml():

    with open(
        "config/commands.yaml",
        "r",
        encoding="utf-8"
    ) as f:

        return yaml.safe_load(f)


def _speak_dynamic_time(time_text):

    with open(
        "config/config.json",
        "r",
        encoding="utf-8"
    ) as f:

        config = json.load(f)

    with tempfile.NamedTemporaryFile(
        suffix=".wav",
        delete=False
    ) as wavfile:

        wav_path = wavfile.name

    subprocess.run(
        [
            config["piper_exe"],
            "-m",
            config["piper_model"],
            "-f",
            wav_path
        ],
        input=time_text,
        text=True,
        check=True
    )

    data, samplerate = sf.read(
        wav_path
    )

    sd.play(
        data,
        samplerate
    )

    sd.wait()


def _run_workflow(workflow_steps):

    yaml_config = _load_yaml()

    commands = yaml_config.get(
        "commands",
        {}
    )

    for step in workflow_steps:

        if step in commands:

            print(
                f"WORKFLOW COMMAND: {commands[step]}"
            )

            subprocess.Popen(
                commands[step],
                shell=True
            )

        else:

            print(
                f"WORKFLOW STEP NOT FOUND: {step}"
            )


def execute(intent):

    print(
        f"ACTION_INTENT: {intent}"
    )

    name = intent["intent"]

    #
    # Generic command execution
    #

    if name == "command":

        print(
            f"COMMAND: {intent['command']}"
        )

        speak(
            "assets/opening_application.wav"
        )

        subprocess.Popen(
            intent["command"],
            shell=True
        )

        return "Command executed"

    #
    # Workflow
    #

    if name == "workflow":

        print(
            f"WORKFLOW: {intent['steps']}"
        )

        speak(
            "assets/opening_application.wav"
        )

        _run_workflow(
            intent["steps"]
        )

        return "Workflow completed"

    #
    # Time
    #

    if name == "time":

        now = datetime.datetime.now()

        time_text = now.strftime(
            "%I %M %p"
        ).lstrip("0")

        _speak_dynamic_time(
            f"The current time is {time_text}"
        )

        return (
            f"Current time is {time_text}"
        )

    #
    # Volume Mute
    #

    if name == "mute":

        speak(
            "assets/volume_muted.wav"
        )

        subprocess.run(
            [
                "powershell",
                "-Command",
                "(New-Object -ComObject WScript.Shell).SendKeys([char]173)"
            ]
        )

        return "Volume muted"

    #
    # Exit Assistant
    #

    if name == "exit":

        speak(
            "assets/exiting_assistant.wav"
        )

        return "__EXIT__"

    #
    # Unknown
    #

    speak(
        "assets/unknown_command.wav"
    )

    return "Unknown command"