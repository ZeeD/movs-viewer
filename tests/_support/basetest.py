from typing import Final
from typing import override
from unittest import TestCase

from PySide6.QtCore import QCoreApplication
from PySide6.QtCore import Qt
from PySide6.QtQuick import QQuickWindow
from PySide6.QtQuick import QSGRendererInterface
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QWidget


class BaseTest(TestCase):
    app: QApplication
    widgets: Final[list[QWidget]] = []

    @override
    @classmethod
    def setUpClass(cls) -> None:
        QCoreApplication.setAttribute(
            Qt.ApplicationAttribute.AA_ShareOpenGLContexts
        )
        QQuickWindow.setGraphicsApi(QSGRendererInterface.GraphicsApi.OpenGLRhi)

        cls.app = QApplication([])

    @override
    @classmethod
    def tearDownClass(cls) -> None:
        for widget in cls.widgets:
            widget.show()
        cls.app.exec()
