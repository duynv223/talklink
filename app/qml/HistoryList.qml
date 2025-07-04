import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: historyList
    width: parent ? parent.width : 400
    color: "#fff"
    radius: 8
    border.color: "#e0e0e0"
    border.width: 1
    clip: true

    // Properties
    property bool sidebarVisible: false
    property bool initializedSidebar: false

    signal conversationOpened()

    ListView {
        id: listView
        anchors.fill: parent
        anchors.margins: 10
        boundsBehavior: Flickable.StopAtBounds
        model: historyModel

        delegate: Rectangle {
            width: listView.width
            height: contentColumn.height + 20
            color: index % 2 === 0 ? "#f9f9f9" : "#ffffff"
            border.color: "#e0e0e0"
            border.width: 1
            radius: 5
            
            Column {
                id: contentColumn
                width: parent.width - 20
                anchors.centerIn: parent
                spacing: 10
                
                RowLayout {
                    width: parent.width
                    spacing: 10
                    
                    // Date and time
                    Text {
                        text: model.date
                        font.pixelSize: 13
                        font.bold: true
                        Layout.preferredWidth: 150
                    }
                    
                    Item { Layout.fillWidth: true }
                    
                    // Open button
                    Button {
                        text: "Open"
                        implicitWidth: 80
                        onClicked: {
                            conversationModel.loadConversation(model.id)
                            historyList.conversationOpened()
                        }
                    }
                }
                
                // Conversation preview
                Rectangle {
                    width: parent.width
                    height: previewText.height + 16
                    color: "#f5f5f5"
                    radius: 4
                    
                    Text {
                        id: previewText
                        width: parent.width - 16
                        anchors.centerIn: parent
                        text: model.preview
                        font.pixelSize: 12
                        wrapMode: Text.WordWrap
                        elide: Text.ElideRight
                        maximumLineCount: 2
                    }
                }
            }
        }

        ScrollBar.vertical: ScrollBar {
            policy: ScrollBar.AsNeeded
        }
        
        // Empty state
        Text {
            anchors.centerIn: parent
            text: "No conversation history"
            font.pixelSize: 16
            color: "#999"
            visible: listView.count === 0
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
                onClicked: conversationModel.clear()
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
        }
    }

    // Rename Speaker SideBar
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
    }

    onSidebarVisibleChanged: {
        if (initializedSidebar) {
            speakerSidebar.isVisible = sidebarVisible
            if (sidebarVisible) {
                speakerSidebar.speakerModel = conversationModel.getUniqueSpeakerMaps()
            }
        }
    }
}
