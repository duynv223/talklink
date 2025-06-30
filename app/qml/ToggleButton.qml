import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: iconBtn
    property alias iconSource: icon.source
    property alias iconWidth: icon.width
    property alias iconHeight: icon.height
    property alias label: btnLabel.text
    property bool showLabel: true
    property bool enabled: true
    property bool active: false
    signal clicked

    width: contentRow.implicitWidth + 16
    height: Math.max(contentRow.implicitHeight, 32)

    Rectangle {
        id: bg
        anchors.fill: parent

        color: {
            if (!iconBtn.enabled)
                return "#e0e0e0";
            else if (mouseArea.pressed)
                return iconBtn.active ? "#aaaaaa" : "#dddddd";
            else
                return iconBtn.active ? "#cccccc" : "#f8f8f8";
        }

        border.color: "#cccccc"
        border.width: 1
        radius: 6
    }

    Row {
        id: contentRow
        anchors.centerIn: parent
        spacing: 6

        Image {
            id: icon
            source: ""
            width: 20
            height: 20
            fillMode: Image.PreserveAspectFit
            visible: icon.source !== ""
        }

        Text {
            id: btnLabel
            text: ""
            visible: iconBtn.showLabel
            color: "#444"
            font.pixelSize: 15
        }
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        enabled: iconBtn.enabled
        cursorShape: Qt.PointingHandCursor
        onClicked: iconBtn.clicked()
    }
}
