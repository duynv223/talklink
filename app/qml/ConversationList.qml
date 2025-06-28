import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    width: parent ? parent.width : 400
    color: "#fff"
    radius: 8
    border.color: "#e0e0e0"
    border.width: 1
    clip: true

    ListView {
        id: listView
        anchors.fill: parent
        anchors.margins: 10
        model: conversationModel

        delegate: Column {
            width: listView.width
            spacing: 2

            TextEdit {
                text: model.speaker + ":"
                font.bold: true
                font.italic: model.speaker === "System"
                color: model.speaker === "System"
                    ? "#888"
                    : (model.speaker.toLowerCase().indexOf("translated") !== -1 ? "#1976d2" : "#1976d2")
                font.pixelSize: 13
                readOnly: true
                selectByMouse: true
                wrapMode: TextEdit.Wrap
                width: parent.width
                padding: 0
            }

            TextEdit {
                text: model.text
                font.pixelSize: 13
                font.italic: model.speaker === "System"
                color: model.speaker === "System"
                    ? "#888"
                    : (model.speaker.toLowerCase().indexOf("translated") !== -1 ? "#1976d2" : "#222")
                readOnly: true
                selectByMouse: true
                wrapMode: TextEdit.Wrap
                width: parent.width
                padding: 0
            }

            Rectangle {
                height: 1
                width: parent.width
                color: "#eee"
            }
        }

        footer: Item { width: 1; height: 100 }

        ScrollBar.vertical: ScrollBar {
            policy: ScrollBar.AsNeeded
        }

        onCountChanged: {
            if (count > 0)
                listView.positionViewAtEnd()
        }
    }
}
