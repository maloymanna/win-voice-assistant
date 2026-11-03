# Version: v1.5.0

import re
import urllib.parse

import yaml


with open(
    "config/commands.yaml",
    "r",
    encoding="utf-8"
) as f:

    CONFIG = yaml.safe_load(f)


COMMANDS = CONFIG.get("commands", {})
CLOSE = CONFIG.get("close", {})
WORKFLOWS = CONFIG.get("workflows", {})
EXIT = CONFIG.get("exit", {})
ALIASES = CONFIG.get("aliases", {})
SEARCH_PREFIXES = ["search web"] + CONFIG.get("search_prefixes", [])


REQUIRED_SECTIONS = [
    "commands",
    "close",
    "aliases",
    "workflows",
    "exit"
]

for section in REQUIRED_SECTIONS:

    if section not in CONFIG:

        raise RuntimeError(
            f"commands.yaml missing section: {section}"
        )


PYTHON_MARKERS = {
    "take screenshot": "__TAKE_SCREENSHOT__",
}


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


def _build_search_intent(query):

    encoded = urllib.parse.quote(
        query,
        safe=""
    )

    base = COMMANDS["search web"]

    return {
        "intent": "command",
        "name": "search web",
        "command": base + encoded
    }


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
    # Python-handled marker commands
    #

    if text in PYTHON_MARKERS:

        result = {
            "intent": "marker",
            "name": text,
            "marker": PYTHON_MARKERS[text],
            "spoken_text": text
        }

        print(
            f"MATCHED INTENT: {result}"
        )

        return result

    #
    # Exact shell command
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
    # Close application
    #

    if text in CLOSE:

        result = {
            "intent": "close",
            "name": text,
            "process": CLOSE[text]
        }

        print(
            f"MATCHED INTENT: {result}"
        )

        return result

    #
    # Search prefixes (search web / google / search / search the web)
    #

    for prefix in SEARCH_PREFIXES:

        if text == prefix:

            result = _build_search_intent("")

            print(
                f"MATCHED INTENT: {result}"
            )

            return result

        if text.startswith(prefix + " "):

            query = text[len(prefix):].strip()

            result = _build_search_intent(query)

            print(
                f"MATCHED INTENT: {result}"
            )

            return result

    print(
        f"NO MATCH FOUND: [{text}]"
    )

    return {
        "intent": "unknown",
        "spoken_text": text
    }