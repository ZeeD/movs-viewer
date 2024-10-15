from contextlib import contextmanager
from typing import TYPE_CHECKING
from typing import Final

from PySide6.QtCore import QCoreApplication
from PySide6.QtCore import Qt
from PySide6.QtQuick import QQuickWindow
from PySide6.QtQuick import QSGRendererInterface
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QWidget

if TYPE_CHECKING:
    from collections.abc import Iterator


@contextmanager
def tmp_app() -> 'Iterator[list[QWidget]]':
    QCoreApplication.setAttribute(
        Qt.ApplicationAttribute.AA_ShareOpenGLContexts
    )
    QQuickWindow.setGraphicsApi(
        QSGRendererInterface.GraphicsApi.OpenGLRhi  # @UndefinedVariable
    )

    app: Final = QApplication([])
    widgets: Final[list[QWidget]] = []
    try:
        yield widgets
    finally:
        for widget in widgets:
            widget.show()
        app.exec()
