# Version: v1.1.0

from PySide6.QtCore import Signal
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QMenu, QSystemTrayIcon


class AssistantTray:

    exit_requested = Signal()

    def __init__(self, idle_icon, listening_icon):

        self.idle_icon_path = idle_icon
        self.listening_icon_path = listening_icon

        self.tray = QSystemTrayIcon(
            QIcon(self.idle_icon_path)
        )

        self.tray.setToolTip("Voice Assistant")

        #
        # Context menu (keep references as instance attributes
        # so Python does not garbage-collect them)
        #

        self.menu = QMenu()

        self.exit_action = QAction("Exit", self.menu)

        self.exit_action.triggered.connect(
            self._request_exit
        )

        self.menu.addAction(self.exit_action)

        self.tray.setContextMenu(self.menu)

    def _request_exit(self):

        self.exit_requested.emit()

    def set_idle(self):

        self.tray.setIcon(QIcon(self.idle_icon_path))

    def set_listening(self):

        self.tray.setIcon(QIcon(self.listening_icon_path))

    def show(self):

        self.tray.show()