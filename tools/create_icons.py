from PIL import Image

SIZE = (32, 32)

# Idle (light gray)
idle = Image.new(
    "RGBA",
    SIZE,
    (192, 192, 192, 255)
)

idle.save("assets/tray_idle.ico")

# Listening (bright green)
listening = Image.new(
    "RGBA",
    SIZE,
    (0, 255, 0, 255)
)

listening.save("assets/tray_listening.ico")

print("Icons created")