#!/bin/sh
# Semi-automatic test of pqp pause and shutdown functionality

set -eu

# Create temporary component files
TEMPDIR=$(mktemp -d)
COMPONENT=$TEMPDIR/Test.qml
echo "import QtQuick 2.7; Rectangle { width: 200; height: 100; color: 'red' }" > "$COMPONENT"

ANOTHER_COMPONENT=$TEMPDIR/TestCopy.qml
cp "$COMPONENT" "$ANOTHER_COMPONENT"

# Lauch pqp and load component
pqp &
sleep 1
pqpc "$COMPONENT"
sleep 1

echo "Turn background green..."
sed -i 's/red/green/' "$COMPONENT"
sleep 1

# Ask for user interaction. Follow instructions printed on screen
echo "Press pause within 3..."
sleep 1
echo "2..."
sleep 1
echo "1..."
sleep 1
echo "None of the following changes should happen."

echo "Turn background blue..."
sed -i 's/green/blue/' "$COMPONENT"
sleep 1

echo "Now resume. You should see a blue rectangle."
sleep 5

pqpc "$ANOTHER_COMPONENT"
sleep 1

echo "Introducing syntax error..."
sed -i 's/red/unicorn/' "$ANOTHER_COMPONENT"
sleep 1

echo "Now close current tab..."
sleep 5

killall pqp
rm -rf "$TEMPDIR"
