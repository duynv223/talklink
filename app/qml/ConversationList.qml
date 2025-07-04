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

    // Properties
    property bool sidebarVisible: false
    property bool initializedSidebar: false
    property var uniqueSpeakers: ListModel {}

    ListView {
        id: listView
        anchors.fill: parent
        anchors.margins: 10
        boundsBehavior: Flickable.StopAtBounds
        model: conversationModel

        delegate: Column {
            width: listView.width
            spacing: 2
            property string messageId: model.id || index

            // Timestamp and Speaker Row
            Row {
                width: parent.width
                spacing: 5

                // Time Stamp
                TextEdit {
                    text: {
                        if (model.timestamp) {
                            var parts = model.timestamp.split(" ");
                            if (parts.length > 1) {
                                return parts[1].substring(0, 8); // Return HH:MM:SS
                            }
                            return model.timestamp;
                        }
                        return "";
                    }
                    font.pixelSize: 12
                    color: "#666"
                    readOnly: true
                    selectByMouse: true
                    wrapMode: TextEdit.NoWrap
                    width: 70
                    padding: 0
                }

                // Speaker Name
                TextEdit {
                    text: model.direction + ":"
                    font.bold: true
                    font.italic: model.direction === "System"
                    color: model.direction === "System"
                        ? "#888"
                        : (model.direction.toLowerCase().indexOf("translated") !== -1 ? "#1976d2" : "#1976d2")
                    font.pixelSize: 13
                    readOnly: true
                    selectByMouse: true
                    wrapMode: TextEdit.Wrap
                    width: parent.width - 75
                    padding: 0
                }
            }

            // Content Column (includes both original and translated text)
            Column {
                width: parent.width
                spacing: 2
                leftPadding: 75

                // Origin Text
                TextEdit {
                    text: model.originText
                    font.pixelSize: 13
                    font.italic: model.direction === "System"
                    color: "#333"
                    readOnly: true
                    selectByMouse: true
                    wrapMode: TextEdit.Wrap
                    width: parent.width - 75
                    padding: 0
                }

                Rectangle {
                    height: 1
                    width: parent.width
                    color: "#eee"
                }

                // Translated Text
                TextEdit {
                    text: model.translatedText || ""
                    font.pixelSize: 13
                    font.italic: true
                    color: "#aaaaaa"
                    readOnly: true
                    selectByMouse: true
                    wrapMode: TextEdit.Wrap
                    width: parent.width - 75
                    padding: 0
                    // visible: text.length > 0 // Only show if there's translated text
                }
            }
        }

        // Footer
        footer: Item { width: 1; height: 60 }

        ScrollBar.vertical: ScrollBar {
            policy: ScrollBar.AsNeeded
        }

        onCountChanged: {
            if (count > 0)
                listView.positionViewAtEnd()
        }
    }

    // Conversation Action
    Item {
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        height: 60
        width: buttonRow.width + 30
        z: 100

        Row {
            id: buttonRow
            spacing: 10
            anchors.centerIn: parent

            IconButton {
                id: summaryConversationButton
                iconSource: "../assets/conversation_action/clear-12.svg"
                onClicked: model.clear()
            }
            IconButton {
                id: renameSpeakerButton
                iconSource: "../assets/conversation_action/rename-15.svg"
                onClicked: {
                    sidebarVisible = !sidebarVisible
                }
            }
            IconButton {
                id: newConversationButton
                iconSource: "../assets/conversation_action/add-90.svg"
                onClicked: {
                    // TODO: Thêm logic đổi tên
                }
            }
        }
    }

    RenameSpeakerSideBar {
        id: speakerSidebar
        visible: true
        speakerModel: uniqueSpeakers
        onSpeakerRenamed: function(speakerId, newName) {
            for (var i = 0; i < conversationModel.count; i++) {
                if (conversationModel.get(i).speaker === speakerId) {
                    conversationModel.setProperty(i, "speaker", newName)
                }
            }
        }
        onHideSidebar: {
            sidebarVisible = false
        }
    }

    Component.onCompleted: {
        initializedSidebar = true
    }

    onSidebarVisibleChanged: {
        if (initializedSidebar) {
            speakerSidebar.isVisible = sidebarVisible
            if (sidebarVisible) {
                updateUniqueSpeakers()
            }
        }
    }

    // Update Speaker
    function updateUniqueSpeakers() {
        uniqueSpeakers.clear()
        var speakers = {}

        for (var i = 0; i < conversationModel.count; i++) {
            var speaker = conversationModel.get(i).speaker
            if (!speakers[speaker]) {
                speakers[speaker] = true
                uniqueSpeakers.append({
                    "speakerId": speaker,
                    "speakerName": speaker
                })
            }
        }
    }
}
