# Version: v1.0.9

import json


def load_commands():

    with open(
        "config/commands.json",
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


COMMANDS = load_commands()


def detect_intent(text):

    text = text.lower()

    print(f"INTENT_MATCH_START: [{text}]")

    for key in COMMANDS:

        if key in text:

            print(
                f"MATCHED COMMAND: [{key}]"
            )

            print(
                f"MATCHED INTENT: [{COMMANDS[key]}]"
            )

            return COMMANDS[key]

    print("NO MATCH FOUND")

    return {
        "intent": "unknown"
    }