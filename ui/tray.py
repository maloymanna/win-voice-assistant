# Version: v1.2.0

from PySide6.QtWidgets import (
    QSystemTrayIcon,
    QMenu,
    QApplication
)

from PySide6.QtGui import (
    QAction,
    QIcon
)


class AssistantTray:

    def __init__(
        self,
        idle_icon,
        listening_icon
    ):

        self.idle_icon = QIcon(
            idle_icon
        )

        self.listening_icon = QIcon(
            listening_icon
        )

        self.tray = QSystemTrayIcon(
            self.idle_icon
        )

        menu = QMenu()

        exit_action = QAction("Exit")

        exit_action.triggered.connect(
            QApplication.instance().quit
        )

        menu.addAction(
            exit_action
        )

        self.tray.setContextMenu(
            menu
        )

    def set_idle(self):

        self.tray.setIcon(
            self.idle_icon
        )

    def set_listening(self):

        self.tray.setIcon(
            self.listening_icon
        )

    def show(self):

        self.tray.show()