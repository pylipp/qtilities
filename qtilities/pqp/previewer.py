#! /usr/bin/env python
"""pqp - Python QML previewer"""

import sys
import os
import argparse

from PyQt5.QtGui import QFont
from PyQt5.QtQuick import QQuickView
from PyQt5.QtCore import QUrl, QTimer, Qt
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QApplication, QMainWindow,\
    QPushButton, QLabel, QTabWidget, QFileDialog
from PyQt5.QtNetwork import QUdpSocket, QHostAddress

from . import UDP_PORT

DEFAULT_FONT = "Ubuntu Condensed"


class PreviewTab(QWidget):
    """Preview of QML component given by 'source' argument. Repeatedly updates
    view unless paused. Potential errors in the QML code are displayed in
    red."""

    def __init__(self, source=None, update_interval=2, parent=None):
        """Args:
        update_interval: in seconds
        """
        super().__init__(parent=parent)

        self.qml_view = QQuickView()
        # idea from
        # https://www.ics.com/blog/combining-qt-widgets-and-qml-qwidgetcreatewindowcontainer
        self.container = QWidget.createWindowContainer(self.qml_view, self)

        self.error_info = QLabel()
        self.error_info.setWordWrap(True)

        self.qml_source = QUrl() if source is None else QUrl(source)
        self.update_source()

        self.pause_button = QPushButton("Pause")
        self.pause_button.setCheckable(True)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.error_info)
        layout.addWidget(self.container)
        layout.addWidget(self.pause_button)

        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.setInterval(update_interval * 1000)

        self.pause_button.clicked.connect(self.toggle_updating)
        self.qml_view.statusChanged.connect(self.check_status)
        self.timer.timeout.connect(self.update_source)

        self.timer.start()

    def toggle_updating(self, clicked):
        self.pause_button.setText("Resume" if clicked else "Pause")
        if clicked:
            self.timer.stop()
        else:
            self.timer.start()

    def update_source(self):
        # idea from
        # https://stackoverflow.com/questions/17337493/how-to-reload-qml-file-to-qquickview
        self.qml_view.setSource(QUrl())
        self.qml_view.engine().clearComponentCache()
        self.qml_view.setSource(self.qml_source)
        self.container.setMinimumSize(self.qml_view.size())
        self.container.setMaximumSize(self.qml_view.size())
        # avoid error label making the window too wide
        self.error_info.setMaximumWidth(self.container.maximumWidth())

    def check_status(self, status):
        if status == QQuickView.Error:
            self.error_info.setText(
                "<font color='red'>{}</font>".format(
                    self.qml_view.errors()[-1].toString()))
        else:
            self.error_info.clear()

    def shutdown(self):
        """Shutdown tab to prepare for removal. Manually delete QML related
        members to free resources. Otherwise error messages are printed even
        after closing the tab, indicating that the QML engine still runs in the
        background.
        """
        # Stop timer to avoid calling update() which requires qml_view which
        # might already be deleted.
        self.timer.stop()
        del self.container
        del self.qml_view


class PreviewWindow(QMainWindow):
    """Displays several QML previews in tabs. Loading new sources is possible
    add start-up, via a FileDialog or by running pqpc which will make the
    internal UDP socket read new sources.
    """

    def __init__(self, *sources, **kwargs):
        """Arguments:
        sources: paths of QML component sources
        kwargs: passed on to PreviewTab
        """
        super().__init__()

        self._tab_kwargs = kwargs
        self.setWindowTitle("pqp")

        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self._populate_tab_widget(*sources)
        self.load_button = QPushButton("Load...")

        layout = QVBoxLayout()
        layout.addWidget(self.tab_widget)
        layout.addWidget(self.load_button)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.udp_socket = QUdpSocket()
        self.udp_socket.bind(QHostAddress.LocalHost, UDP_PORT)

        self.load_button.clicked.connect(self.show_dialog)
        self.udp_socket.readyRead.connect(self.read_from_udp_client)
        self.tab_widget.tabCloseRequested.connect(self.shutdown_tab)

    def _populate_tab_widget(self, *sources):
        for source in sources:
            self.tab_widget.addTab(
                PreviewTab(source=source, parent=self, **self._tab_kwargs),
                os.path.basename(source))
        if sources:
            # focus tab that was added last
            self.tab_widget.setCurrentIndex(self.tab_widget.count() - 1)

    def show_dialog(self, _):
        sources = QFileDialog.getOpenFileNames(
                caption="Select file(s) to load", filter="(*.qml)",
                directory=os.getcwd())[0]
        self._populate_tab_widget(*sources)

    def read_from_udp_client(self):
        while self.udp_socket.hasPendingDatagrams():
            data, _, _ = self.udp_socket.readDatagram(
                self.udp_socket.pendingDatagramSize())
            sources = [d.decode("utf-8") for d in data.splitlines()]
            self._populate_tab_widget(*sources)

    def shutdown_tab(self, index):
        """Shutdown and remove the tab at given index."""
        selected_tab = self.tab_widget.widget(index)
        selected_tab.shutdown()
        self.tab_widget.removeTab(index)


def main():
    parser = argparse.ArgumentParser(description=globals()["__doc__"])

    parser.add_argument(
        "source", nargs="*", help="zero or more source file(s) to preview")
    parser.add_argument(
        "--font",
        help="specify application font (default: {})".format(DEFAULT_FONT),
        default=DEFAULT_FONT)

    cl_arguments = parser.parse_args()

    app = QApplication([])

    font = QFont()
    font.setFamily(cl_arguments.font)
    app.setFont(font)

    window = PreviewWindow(*cl_arguments.source)
    window.show()
    sys.exit(app.exec_())
