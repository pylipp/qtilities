#! /usr/bin/env python
import os.path
import sys

from PyQt5.QtGui import QGuiApplication
from PyQt5.QtCore import QUrl
from PyQt5.QtQuick import QQuickView
from PyQt5.QtQml import QQmlEngine, QQmlComponent


def main():
    # Alternative?
    # https://github.com/qt/qtdeclarative/blob/5.11/tools/qmlscene/main.cpp#L595

    app = QGuiApplication([])

    try:
        path = QUrl(sys.argv[1])
    except IndexError:
        print("Usage: {} QMLFILE".format(os.path.basename(sys.argv[0])))
        sys.exit(1)

    view = QQuickView(path)

    view.show()
    sys.exit(app.exec_())
