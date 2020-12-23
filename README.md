# qtilities

A collection of utility programs for PyQt5 development.

## Installation

### From PyPI

    pip install qtilities

### From source

    git clone https://github.com/pylipp/qtilities
    cd qtilities
    make install

## Contents

### `pqp` and `pqpc`

> Python QML Previewer and Client

`pqp` previews QML components and continuously updates while you're editing the source code.

#### Start

Launch an empty previewer:

    > pqp

Launch the previewer displaying one or more components by providing the paths:

    > pqp TextFoo.qml bar/ComboBaz.qml

#### Loading components

Load components by clicking the 'Load' button.

Alternatively you can run the client:

    > pqpc HackWindow.qml

It sends one or more component paths via UDP to port 31415. The previewer `pqp` listens to that port and loads the components.

#### Pausing/resuming preview

`pqp` continuously updates, regardless of changes in the source code or not. If you wish to test user interaction functionality of your component, you can pause the preview by clicking the 'Preview' button.

### `qmltags`

> Basic ctags generator for QML components

`qmltags` generates 'class' ctags for custom QML components, and 'method' ctags for 'function's.

Run without arguments to recursively parse the current directory and its subdirectories for QML files

    > qmltags

Alternatively, you can provide one or more paths to QML components:

    > qmltags HackWindow.qml screen/*.qml

This assumes that your shell performs file name expansion.

Note that `qmltags` overwrites a `qmltags` file in the current working directory if it exists. You can specify a custom output filepath:

    > qmltags HackWindow.qml screen/*.qml -o mytags

#### Editor integration

Configure `vim` to take the generated `qmltags` file into account:

    set tags=./tags,./qmltags;$HOME

### `pyqmlscene`

> Basic Python port of the `qmlscene` utility

Run with a QML file holding an arbitrary component as argument:

    > pyqmlscene MyComponent.qml

## Development

### Set up

    python3 -m venv .venv
    source .venv/bin/activate
    pip install -U pip
    pip install -U -e .

### Testing

    source .venv/bin/activate
    python -m unittest

### Release

1. Add git tag with bumped version number.
1. Run `make publish`.
