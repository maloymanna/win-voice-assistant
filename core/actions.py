# Version: v1.2.2

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

    apps = yaml_config.get(
        "apps",
        {}
    )

    urls = yaml_config.get(
        "urls",
        {}
    )

    aliases = yaml_config.get(
        "aliases",
        {}
    )

    for step in workflow_steps:

        step = aliases.get(
            step,
            step
        )

        if step in apps:

            subprocess.Popen(
                apps[step]["target"]
            )

        elif step in urls:

            subprocess.Popen(
                [
                    "cmd",
                    "/c",
                    "start",
                    "",
                    urls[step]["target"]
                ],
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

    if name == "open_app":

        print(
            f"OPEN_APP TARGET: {intent['target']}"
        )

        speak(
            "assets/opening_application.wav"
        )

        subprocess.Popen(
            intent["target"]
        )

        return "Opening application"

    if name == "open_url":

        print(
            f"OPEN_URL TARGET: {intent['target']}"
        )

        speak(
            "assets/opening_application.wav"
        )

        subprocess.Popen(
            [
                "cmd",
                "/c",
                "start",
                "",
                intent["target"]
            ],
            shell=True
        )

        return "Opening website"

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

    if name == "exit":

    speak(
        "assets/exiting_assistant.wav"
    )

    return "__EXIT__"


    speak(
        "assets/unknown_command.wav"
    )

    return "Unknown command"