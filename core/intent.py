# Version: v1.3.0

import re
import yaml


with open(
    "config/commands.yaml",
    "r",
    encoding="utf-8"
) as f:

    CONFIG = yaml.safe_load(f)


COMMANDS = CONFIG.get(
    "commands",
    {}
)

WORKFLOWS = CONFIG.get(
    "workflows",
    {}
)

EXIT = CONFIG.get(
    "exit",
    {}
)

ALIASES = CONFIG.get(
    "aliases",
    {}
)


REQUIRED_SECTIONS = [
    "commands",
    "aliases",
    "workflows",
    "exit"
]

for section in REQUIRED_SECTIONS:

    if section not in CONFIG:

        raise RuntimeError(
            f"commands.yaml missing section: {section}"
        )


def _normalize(text):

    text = text.lower()

    timestamp_pattern = (
        r"\[\d{2}:\d{2}:\d{2}\.\d+"
        r"\s*-->\s*"
        r"\d{2}:\d{2}:\d{2}\.\d+\]"
    )

    text = re.sub(
        timestamp_pattern,
        "",
        text
    )

    text = re.sub(
        r"[^a-z0-9\-\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    return text


def _resolve_alias(text):

    return ALIASES.get(
        text,
        text
    )


def detect_intent(text):

    text = _normalize(text)

    text = _resolve_alias(
        text
    )

    print(
        f"INTENT_MATCH_START: [{text}]"
    )

    #
    # Exit
    #

    if text in EXIT:

        result = {
            "intent": "exit"
        }

        print(
            f"MATCHED INTENT: {result}"
        )

        return result

    #
    # Workflow
    #

    if text in WORKFLOWS:

        result = {
            "intent": "workflow",
            "name": text,
            "steps": WORKFLOWS[text]
        }

        print(
            f"MATCHED INTENT: {result}"
        )

        return result

    #
    # Command
    #

    if text in COMMANDS:

        result = {
            "intent": "command",
            "name": text,
            "command": COMMANDS[text]
        }

        print(
            f"MATCHED INTENT: {result}"
        )

        return result

    #
    # Built-ins
    #

    if text == "what time is it":

        return {
            "intent": "time"
        }

    if text == "mute volume":

        return {
            "intent": "mute"
        }

    print(
        f"NO MATCH FOUND: [{text}]"
    )

    return {
        "intent": "unknown",
        "spoken_text": text
    }