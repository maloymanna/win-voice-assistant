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

    for key in COMMANDS:
        if key in text:
            return COMMANDS[key]

    return {
        "intent": "unknown"
    }
