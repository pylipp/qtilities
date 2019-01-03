#! /usr/bin/env python
"""pyqmlscene - Basic Python port of the qmlscene utility"""

import sys

from PyQt5.QtGui import QGuiApplication
from PyQt5.QtCore import QUrl
from PyQt5.QtQuick import QQuickView, QQuickWindow, QQuickItem
from PyQt5.QtQml import QQmlApplicationEngine, QQmlComponent


def main():
    app = QGuiApplication([])

    try:
        path = QUrl(sys.argv[1])
    except IndexError:
        print("Usage: pyqmlscene <filename>")
        sys.exit(1)

    engine = QQmlApplicationEngine()

    # Procedure similar to
    # https://github.com/qt/qtdeclarative/blob/0e9ab20b6a41bfd40aff63c9d3e686606e51e798/tools/qmlscene/main.cpp
    component = QQmlComponent(engine)
    component.loadUrl(path)
    root_object = component.create()

    if isinstance(root_object, QQuickWindow):
        # Display window object
        root_object.show()
    elif isinstance(root_object, QQuickItem):
        # Display arbitrary QQuickItems by reloading the source since
        # reparenting the existing root object to the view did not have any
        # effect. Neither does the QQuickView class have a setContent() method
        view = QQuickView(path)
        view.show()
    else:
        raise SystemExit("Error displaying {}".format(root_object))

    sys.exit(app.exec_())
