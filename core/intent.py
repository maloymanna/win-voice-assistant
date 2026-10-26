# Version: v1.1.0

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


def _resolve_alias(name):

    return ALIASES.get(
        name,
        name
    )


def detect_intent(text):

    text = text.lower().strip()

    print(
        f"INTENT_MATCH_START: [{text}]"
    )

    if text.startswith("open "):

        thing = text[5:].strip()

        thing = _resolve_alias(
            thing
        )

        if thing in APPS:

            return {
                "intent": "open_app",
                "name": thing,
                "target": APPS[thing]["target"]
            }

        if thing in URLS:

            return {
                "intent": "open_url",
                "name": thing,
                "target": URLS[thing]["target"]
            }

    if text.startswith("go to "):

        thing = text[6:].strip()

        thing = _resolve_alias(
            thing
        )

        if thing in URLS:

            return {
                "intent": "open_url",
                "name": thing,
                "target": URLS[thing]["target"]
            }

    if text in WORKFLOWS:

        return {
            "intent": "workflow",
            "name": text,
            "steps": WORKFLOWS[text]
        }

    if text == "what time is it":

        return {
            "intent": "time"
        }

    if text == "mute volume":

        return {
            "intent": "mute"
        }

    return {
        "intent": "unknown"
    }