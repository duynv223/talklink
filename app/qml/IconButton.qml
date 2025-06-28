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
    property bool spinning: false
    property bool blinking: false
    property color backgroundColor: "#f5f5f5"
    property bool allowSpin: false
    signal clicked

    width: contentRow.implicitWidth + 16
    height: Math.max(contentRow.implicitHeight, 32)

    Rectangle {
        id: bg
        anchors.fill: parent
        radius: 6
        border.color: "#cccccc"
        border.width: 1
        opacity: 1.0
        color: !iconBtn.enabled ? "#eeeeee"
              : mouseArea.containsMouse ? Qt.darker(iconBtn.backgroundColor, 1.1)
              : iconBtn.backgroundColor

        Behavior on color {
            ColorAnimation { duration: 150 }
        }

        SequentialAnimation on opacity {
            running: iconBtn.blinking
            loops: Animation.Infinite
            NumberAnimation { to: 0.6; duration: 400; easing.type: Easing.InOutQuad }
            NumberAnimation { to: 1.0; duration: 400; easing.type: Easing.InOutQuad }
        }
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
            rotation: spinning && allowSpin ? rotation : 0

            RotationAnimator on rotation {
                running: spinning && allowSpin
                from: 0
                to: 360
                loops: Animation.Infinite
                duration: 2000
            }

            Behavior on rotation {
                enabled: !(spinning && allowSpin)
                NumberAnimation {
                    duration: 150
                    easing.type: Easing.OutQuad
                }
            }
        }

        Text {
            id: btnLabel
            text: ""
            visible: iconBtn.showLabel
            color: "#333"
            font.pixelSize: 15
        }
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        enabled: iconBtn.enabled
        cursorShape: Qt.PointingHandCursor
        onClicked: iconBtn.clicked()
    }
}
