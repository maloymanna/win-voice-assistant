# Version: v1.0

from windows_toasts import (
    WindowsToaster,
    Toast
)

toaster = WindowsToaster("Assistant")


def notify(message):

    toast = Toast()

    toast.duration = "short"

    toast.text_fields = [
        "Assistant",
        message
    ]

    toaster.show_toast(toast)