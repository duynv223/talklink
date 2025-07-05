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
                    text: model.timestamp
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
                    text: model.speaker + ":"
                    font.bold: true
                    font.italic: model.direction === "Other"
                    color: model.direction === "Other" ? "#888" : "#2e7d32"
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
                    font.italic: model.direction === "Other"
                    color: model.direction === "Other" ? "#888" : "#2e7d32"
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
                    font.italic: model.direction === "Other"
                    color: model.direction === "Other" ? "#888" : "#2e7d32"
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
                iconSource: "../assets/conversation_action/historical-sumary-svgrepo-com.svg"
                onClicked: showSummary()
            }
            IconButton {
                id: clearConversationButton
                iconSource: "../assets/conversation_action/clear-12.svg"
                onClicked: conversationModel.clear()
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
                onClicked: conversationModel.new_conversation()
            }
        }
    }

    RenameSpeakerSideBar {
        id: speakerSidebar
        visible: true
        speakerModel: []
        onSpeakerRenamed: function(speakerId, newName) {
            conversationModel.updateSpeakerName(speakerId, newName)
        }
        onHideSidebar: {
            sidebarVisible = false
        }
    }

    Component.onCompleted: {
        initializedSidebar = true
    }

    Connections {
        target: conversationModel
        function onUniqueSpeakersChanged() {
            if (sidebarVisible) {
                speakerSidebar.speakerModel = conversationModel.getUniqueSpeakerMaps()
            }
        }
        function onSummaryReady(text) {
            summaryPopup.loading = false
            summaryPopup.result = text
        }

        function onSummaryError(err) {
            summaryPopup.loading = false
            summaryPopup.result = "Lỗi: " + err
        }
    }

    onSidebarVisibleChanged: {
        if (initializedSidebar) {
            speakerSidebar.isVisible = sidebarVisible
            if (sidebarVisible) {
                speakerSidebar.speakerModel = conversationModel.getUniqueSpeakerMaps()
            }
        }
    }

    PopUpSummary {
        id: summaryPopup
        title: "Summary Conversation"
        okText: "Close"
        showCancelButton: false

        Component.onCompleted: {
        }
    }

    function showSummary() {
        summaryPopup.setLoading(true)
        summaryPopup.open()
        conversationModel.summarizeConversation()
    }

    Connections {
        target: conversationModel
        function onSummaryReady(text) {
            summaryPopup.setLoading(false)
            summaryPopup.setResult(text)
        }
        function onSummaryError(err) {
            summaryPopup.setLoading(false)
            summaryPopup.setContent("Error: " + err)
        }
    }
}
