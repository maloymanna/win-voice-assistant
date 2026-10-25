from PySide6.QtWidgets import (
    QSystemTrayIcon,
    QMenu
)
from PySide6.QtGui import QAction

class AssistantTray:

    def __init__(
        self,
        icon,
        listen_callback
    ):
        self.tray = QSystemTrayIcon(icon)

        menu = QMenu()

        exit_action = QAction("Exit")

        exit_action.triggered.connect(
            lambda: quit()
        )

        menu.addAction(exit_action)

        self.tray.setContextMenu(menu)

        self.tray.activated.connect(
            self.on_click
        )

        self.listen_callback = listen_callback

    def on_click(self, reason):

        if reason == QSystemTrayIcon.Trigger:
            self.listen_callback()

    def show(self):
        self.tray.show()
