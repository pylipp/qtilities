#! /usr/bin/env python
"""pqp - Python QML previewer"""

import sys
import os
import argparse
import glob

from PyQt5.QtGui import QFont
from PyQt5.QtQuick import QQuickView
from PyQt5.QtCore import QUrl, Qt, QFileSystemWatcher, QThread
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QApplication, QMainWindow,\
    QPushButton, QLabel, QTabWidget, QFileDialog
from PyQt5.QtNetwork import QUdpSocket, QHostAddress

from . import UDP_PORT

DEFAULT_FONT = "Ubuntu Condensed"


class PreviewTab(QWidget):
    """Preview of QML component given by 'source' argument. If any file in the
    source's directory or one of its subdirectories is changed, the view is
    updated unless paused. Potential errors in the QML code are displayed in
    red."""

    def __init__(self, source=None, parent=None):
        super().__init__(parent=parent)

        self.updating_paused = False

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

        # Observations using the QFileSystemWatcher in various settings:
        # A) fileChanged signal and qml file paths
        #   Collected all *.qml files in the directory of the source and all
        #   subdirectories and added to the watcher. Now the first change would
        #   trigger the signal but none of the following
        # B) additionally connecting directoryChanged signal
        #   same issue
        # C) both signals, (sub)directory file paths
        #   Collected all subdirectories of the source directory and added it to
        #   the watcher, along with the source directory itself. Works as
        #   expected
        # D) directoryChanged signal, (sub)directory file paths
        #   same as C) without fileChanged signal, works as expected
        # Eventual solution: D
        # This implementation also helped me:
        # https://github.com/penk/qml-livereload/blob/master/main.cpp
        self.watcher = QFileSystemWatcher()
        source_dir = os.path.dirname(source)
        source_paths = glob.glob(os.path.join(source_dir, "*/"), recursive=True)
        source_paths.append(source_dir)
        failed_paths = self.watcher.addPaths(source_paths)
        if failed_paths:
            print("Failed to watch paths: {}".format(", ".join(failed_paths)))

        self.pause_button.clicked.connect(self.toggle_updating)
        self.qml_view.statusChanged.connect(self.check_status)
        self.watcher.directoryChanged.connect(self.update_source)

    def toggle_updating(self, clicked):
        """Callback for pause button."""
        self.pause_button.setText("Resume" if clicked else "Pause")
        self.updating_paused = clicked

        # Update when resuming in case of the source having changed
        if not self.updating_paused:
            self.update_source()

    def update_source(self, _=None):
        """Method and callback to update the QML view source. The second
        argument is required to have a slot matching the directoryChanged()
        interface.
        This immediately returns if updating is paused.
        """
        if self.updating_paused:
            return

        # idea from
        # https://stackoverflow.com/questions/17337493/how-to-reload-qml-file-to-qquickview
        self.qml_view.setSource(QUrl())
        self.qml_view.engine().clearComponentCache()
        # avoid error: No such file or directory
        QThread.msleep(50)
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
