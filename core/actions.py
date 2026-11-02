# core/actions.py
# Version: v1.4.0

import subprocess
import datetime
import os
import yaml


def _load_yaml():

    with open(
        "config/commands.yaml",
        "r",
        encoding="utf-8"
    ) as f:

        return yaml.safe_load(f)


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


def _take_screenshot():

    ts = datetime.datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    pictures = os.path.join(
        os.path.expanduser("~"),
        "Pictures"
    )

    os.makedirs(
        pictures,
        exist_ok=True
    )

    path = os.path.join(
        pictures,
        f"Screenshot_{ts}.png"
    )

    ps_script = (
        "Add-Type -AssemblyName System.Windows.Forms,System.Drawing;"
        "$b=[System.Windows.Forms.SystemInformation]::VirtualScreen;"
        "$bmp=New-Object System.Drawing.Bitmap($b.Width,$b.Height);"
        "$g=[System.Drawing.Graphics]::FromImage($bmp);"
        "$g.CopyFromScreen($b.Location,[System.Drawing.Point]::Empty,$b.Size);"
        f"$bmp.Save('{path}');"
    )

    subprocess.run(
        ["powershell", "-Command", ps_script],
        check=True
    )

    print(
        f"SCREENSHOT SAVED: {path}"
    )

    return path


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

        _run_workflow(
            intent["steps"]
        )

        return "Workflow completed"

    #
    # Marker commands handled in Python
    #

    if name == "marker":

        marker = intent.get("marker", "")

        if marker == "__TAKE_SCREENSHOT__":

            path = _take_screenshot()

            return f"Screenshot saved to {path}"

    #
    # Exit Assistant
    #

    if name == "exit":

        return "__EXIT__"

    #
    # Unknown
    #

    return "Unknown command"