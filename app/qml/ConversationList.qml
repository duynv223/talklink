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
            spacing: 2
            Text {
                text: model.speaker + ":"
                font.bold: true
                font.italic: model.speaker === "System"
                color: model.speaker === "System"
                    ? "#888"
                    : (model.speaker.toLowerCase().indexOf("translated") !== -1 ? "#1976d2" : "#1976d2")
                font.pixelSize: 13
            }
            Text {
                text: model.text
                color: model.speaker === "System"
                    ? "#888"
                    : (model.speaker.toLowerCase().indexOf("translated") !== -1 ? "#1976d2" : "#222")
                font.pixelSize: 13
                font.italic: model.speaker === "System"
            }
            Rectangle { height: 1; width: parent.width; color: "#eee" }
        }
        footer: Item { width: 1; height: 100 }
        onCountChanged: {
            if (count > 0)
                listView.positionViewAtEnd()
        }
    }
}
