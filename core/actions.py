# core/actions.py
# Version: v1.6.0

import subprocess
import datetime
import json
import os
import yaml


def _load_config():

    with open(
        "config/config.json",
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


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
                shell=False,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

        else:

            print(
                f"WORKFLOW STEP NOT FOUND: {step}"
            )


def _take_screenshot():

    config = _load_config()

    ts = datetime.datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    target_dir = config.get(
        "screenshot_dir",
        os.path.join(os.path.expanduser("~"), "Pictures")
    )

    os.makedirs(
        target_dir,
        exist_ok=True
    )

    path = os.path.join(
        target_dir,
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
        shell=False,
        creationflags=subprocess.CREATE_NO_WINDOW,
        check=True,
        capture_output=True
    )

    print(
        f"SCREENSHOT SAVED: {path}"
    )

    return path


def _close_process(process):

    if process.lower() == "explorer.exe":

        # Close only file explorer windows, keep taskbar and desktop
        subprocess.run(
            [
                "powershell",
                "-Command",
                "(New-Object -ComObject Shell.Application)"
                ".Windows() | ForEach-Object { $_.Quit() }"
            ],
            shell=False,
            creationflags=subprocess.CREATE_NO_WINDOW,
            capture_output=True
        )

        return "Closed Explorer windows"

    result = subprocess.run(
        ["taskkill", "/f", "/im", process],
        shell=False,
        creationflags=subprocess.CREATE_NO_WINDOW,
        capture_output=True
    )

    if result.returncode == 0:

        return f"Closed {process}"

    return f"Process not running: {process}"


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
            shell=False,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        return "Command executed"

    #
    # Script launch (fire-and-forget)
    #

    if name == "script":

        print(
            f"SCRIPT: {intent['script']}"
        )

        subprocess.Popen(
            intent["argv"],
            shell=False,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        return "Command executed"

    #
    # Close application
    #

    if name == "close":

        return _close_process(
            intent["process"]
        )

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