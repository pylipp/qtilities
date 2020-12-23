import QtQuick 2.7
import QtQuick.Controls 2.3

ApplicationWindow {
    width: 200
    height: 400

    property alias rectColor: rectangle.color
    property bool userLogin

    Rectangle {
        id: rectangle
        anchors.fill: parent
        color: "blue"
    }

    function doNothing() {}

    function doLess(argument) {}

    Item {
        function nested() {}

        property int count: 5
    }
}
