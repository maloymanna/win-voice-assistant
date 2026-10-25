from windows_toasts import Toast

def notify(text):

    toast = Toast()

    toast.text_fields = [
        "Assistant",
        text
    ]

    toast.show()
