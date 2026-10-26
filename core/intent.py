# core/intent.py
# Version: v1.1.3

import re
import yaml


with open(
    "config/commands.yaml",
    "r",
    encoding="utf-8"
) as f:

    CONFIG = yaml.safe_load(f)


APPS = CONFIG.get(
    "apps",
    {}
)

URLS = CONFIG.get(
    "urls",
    {}
)

ALIASES = CONFIG.get(
    "aliases",
    {}
)

WORKFLOWS = CONFIG.get(
    "workflows",
    {}
)


REQUIRED_SECTIONS = [
    "apps",
    "urls",
    "aliases",
    "workflows"
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


def _resolve_alias(name):

    return ALIASES.get(
        name,
        name
    )


def _build_app_intent(name):

    return {
        "intent": "open_app",
        "name": name,
        "target": APPS[name]["target"]
    }


def _build_url_intent(name):

    return {
        "intent": "open_url",
        "name": name,
        "target": URLS[name]["target"]
    }


def detect_intent(text):

    text = _normalize(text)

    print(
        f"INTENT_MATCH_START: [{text}]"
    )

    #
    # workflows first
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
    # direct aliases
    #

    resolved = _resolve_alias(
        text
    )

    if resolved in APPS:

        result = _build_app_intent(
            resolved
        )

        print(
            f"MATCHED INTENT: {result}"
        )

        return result

    if resolved in URLS:

        result = _build_url_intent(
            resolved
        )

        print(
            f"MATCHED INTENT: {result}"
        )

        return result

    #
    # open / launch / start
    #

    for prefix in [
        "open ",
        "launch ",
        "start "
    ]:

        if text.startswith(prefix):

            thing = text[len(prefix):].strip()

            thing = _resolve_alias(
                thing
            )

            if thing in APPS:

                result = _build_app_intent(
                    thing
                )

                print(
                    f"MATCHED INTENT: {result}"
                )

                return result

            if thing in URLS:

                result = _build_url_intent(
                    thing
                )

                print(
                    f"MATCHED INTENT: {result}"
                )

                return result

    #
    # go to <site>
    #

    if text.startswith("go to "):

        thing = text[6:].strip()

        thing = _resolve_alias(
            thing
        )

        if thing in URLS:

            result = _build_url_intent(
                thing
            )

            print(
                f"MATCHED INTENT: {result}"
            )

            return result

    #
    # built-ins
    #

    if text == "what time is it":

        return {
            "intent": "time"
        }

    if text == "mute volume":

        return {
            "intent": "mute"
        }

    if text in [
        "exit",
        "quit",
        "close assistant",
        "shutdown assistant"
    ]:

        return {
            "intent": "exit"
        }

    print(
        f"NO MATCH FOUND: [{text}]"
    )

    return {
        "intent": "unknown",
        "spoken_text": text
    }