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

    property var conversation_data: []

    signal conversationOpened()


//---------------------- History List ----------------------//
    RowLayout {
        anchors.fill: parent
        spacing: 0
        ListView {
            id: history_view
            Layout.preferredWidth: parent ? parent.width * 0.3 : 300
            Layout.fillHeight: true
            Layout.margins: 10
            model: historyModel
            clip: true
            spacing: 12
            boundsBehavior: Flickable.StopAtBounds

            delegate: Rectangle {
                width: history_view.width
                height: contentColumn.height + 32
                color: ListView.isCurrentItem ? "#e3f2fd" : (index % 2 === 0 ? "#f9f9f9" : "#ffffff")
                border.color: ListView.isCurrentItem ? "#2196f3" : "#e0e0e0"
                border.width: 1
                radius: 5
                anchors.leftMargin: 4
                anchors.rightMargin: 4
                anchors.topMargin: 6
                anchors.bottomMargin: 6
                
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
                MouseArea {
                    anchors.fill: parent
                    onClicked: {
                        history_view.currentIndex = index
                        historyModel.changeConversation(model.id)
                    }
                    cursorShape: Qt.PointingHandCursor
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
                visible: history_view.count === 0
            }
        }

        Rectangle {
            width: 1
            color: "#e0e0e0"
            Layout.fillHeight: true
        }

        ConversationView {
            id: conversation_view
            Layout.preferredWidth: parent ? parent.width * 0.7 : 500
            Layout.fillHeight: true
            Layout.margins: 10
            conversationData: historyList.conversation_data
            otherSpeakerColor: "#888"
            userSpeakerColor: "#2e7d32"
        }
    }

    // Conversation Connections
    Connections {
        target: historyModel
        function onConversationDataChanged() {
            historyList.conversation_data = historyModel.getConversationData()
        }
    }

//---------------------- History Action ----------------------//
    ConversationActionBar {
        id: actionBar
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        
        showSummaryButton: true
        showClearButton: false
        showRenameButton: true
        showNewButton: false
        
        onSummaryClicked: showSummary()
        onRenameClicked: sidebarVisible = !sidebarVisible
    }

//---------------------- Rename Speacker Sidebar ----------------------//
    RenameSpeakerSideBar {
        id: speakerSidebar
        visible: true
        speakerModel: []
        onSpeakerRenamed: function(speakerId, newName) {
            historyModel.updateSpeakerName(speakerId, newName)
        }
        onHideSidebar: {
            sidebarVisible = false
        }
    }

    onSidebarVisibleChanged: {
        if (initializedSidebar) {
            speakerSidebar.isVisible = sidebarVisible
            if (sidebarVisible) {
                speakerSidebar.speakerModel = historyModel.getUniqueSpeakerMaps()
            }
        }
    }

    // Rename Speaker Connections
    Connections {
        target: historyModel
        function onUniqueSpeakersChanged() {
            if (sidebarVisible) {
                speakerSidebar.speakerModel = historyModel.getUniqueSpeakerMaps()
            }
        }
    }


//---------------------- Summary PopUp ----------------------//
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
        historyModel.summarizeConversation()
    }

    // Summary PopUp Connections
    Connections {
        target: historyModel
        function onSummaryReady(text) {
            summaryPopup.setLoading(false)
            summaryPopup.setResult(text)
        }
        function onSummaryError(err) {
            summaryPopup.setLoading(false)
            summaryPopup.setContent("Error: " + err)
        }
    }

    // Initialize sidebar and load conversation data
    Component.onCompleted: {
        initializedSidebar = true
        if (historyModel && historyModel.getConversationData) {
            conversation_data = historyModel.getConversationData()
        }

        if (historyModel && historyModel.getUniqueSpeakerMaps) {
            speakerSidebar.speakerModel = historyModel.getUniqueSpeakerMaps()
        }
    }
}
