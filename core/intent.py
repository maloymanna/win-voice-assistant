# Version: v1.1.1

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


def _normalize(text):

    text = text.lower()

    text = re.sub(
        r"[^a-z0-9\-\s]",
        "",
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


def detect_intent(text):

    text = _normalize(text)

    print(
        f"INTENT_MATCH_START: [{text}]"
    )

    if text.startswith("open "):

        thing = text[5:].strip()

        thing = _resolve_alias(
            thing
        )

        if thing in APPS:

            result = {
                "intent": "open_app",
                "name": thing,
                "target": APPS[thing]["target"]
            }

            print(
                f"MATCHED INTENT: {result}"
            )

            return result

        if thing in URLS:

            result = {
                "intent": "open_url",
                "name": thing,
                "target": URLS[thing]["target"]
            }

            print(
                f"MATCHED INTENT: {result}"
            )

            return result

    if text.startswith("go to "):

        thing = text[6:].strip()

        thing = _resolve_alias(
            thing
        )

        if thing in URLS:

            result = {
                "intent": "open_url",
                "name": thing,
                "target": URLS[thing]["target"]
            }

            print(
                f"MATCHED INTENT: {result}"
            )

            return result

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

    if text == "what time is it":

        return {
            "intent": "time"
        }

    if text == "mute volume":

        return {
            "intent": "mute"
        }

    print("NO MATCH FOUND")

    return {
        "intent": "unknown"
    }