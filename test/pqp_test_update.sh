#!/bin/sh
# Automatic test of pqp update functionality

set -eu

# Create temporary component files
TEMPDIR=$(mktemp -d)
COMPONENT=$TEMPDIR/Test.qml
echo "import QtQuick 2.7; import 'stuff'; Rectangle { width: 200; height: 100; color: 'red'; SimpleText { anchors.centerIn: parent; text: 'hello world' } }" > "$COMPONENT"

SUBDIR=$TEMPDIR/stuff
mkdir "$SUBDIR"
SUBCOMPONENT=$SUBDIR/SimpleText.qml
echo "import QtQuick 2.7; Text { color: 'black' }" > "$SUBCOMPONENT"

# Lauch pqp and load component
pqp &
sleep 1
pqpc "$COMPONENT"
sleep 1

# Trigger updates by stream editing source code
echo "Turn background green..."
sed -i 's/red/green/' "$COMPONENT"
sleep 1
echo "Turn background blue..."
sed -i 's/green/blue/' "$COMPONENT"
sleep 1
echo "Now greeting you..."
sed -i 's/world/you/' "$COMPONENT"
sleep 1

echo "Turn font color white..."
sed -i 's/black/white/' "$SUBCOMPONENT"
sleep 1
echo "Turn font color black..."
sed -i 's/white/black/' "$SUBCOMPONENT"
sleep 1

# Shutdown and clean up
killall pqp
rm -rf "$TEMPDIR"
