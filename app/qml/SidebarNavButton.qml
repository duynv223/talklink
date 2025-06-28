import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: navButton
    property bool active: false
    property string iconSource: ""
    property string label: ""
    signal clicked()

    width: 90
    height: 90

    Column {
        anchors.centerIn: parent
        spacing: 5

        Image {
            source: navButton.iconSource
            width: 28
            height: 28
            fillMode: Image.PreserveAspectFit
            anchors.horizontalCenter: parent.horizontalCenter
            visible: navButton.iconSource !== ""
        }

        Text {
            text: navButton.label
            font.pixelSize: 13
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            anchors.horizontalCenter: parent.horizontalCenter
            wrapMode: Text.WordWrap
        }
    }

    Rectangle {
        id: mouseOverlay
        anchors.fill: parent
        color: "#e0e0e0"
        opacity: mouseArea.containsMouse | active ? 1 : 0.4
        radius: 8
        z: -1
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor

        onClicked: {
            navButton.clicked();
        }
    }
}
