# qtilities

A collection of utility programs for PyQt5 development.

## Installation

### From PyPI

    pip install qtilities

### From source

    git clone https://github.com/pylipp/qtilities
    cd qtilities
    make install

## `pqp` and `pqpc`

> Python QML Previewer and Client

`pqp` previews QML components and continuously updates while you're editing the source code.

### Usage

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
