import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: conversationViewRoot
    
    // Đặt các thuộc tính quan trọng để hoạt động trong bố cục Layout
    Layout.fillWidth: true
    Layout.fillHeight: true
    implicitWidth: parent ? parent.width : 400
    
    color: "#fff"
    radius: 8
    border.color: "#e0e0e0"
    border.width: 1
    clip: true

    // Đảm bảo rectangle này lấp đầy không gian được cung cấp
    anchors.margins: 0

    // Properties to be exposed to parent
    property var conversationData: []
    property color otherSpeakerColor: "#888"
    property color userSpeakerColor: "#2e7d32"
    
    // Track if viewing the end of the list
    property bool atEnd: true // Default to true for initial load
    
    // Expose ListView methods
    function scrollToEnd() {
        conversation_view.positionViewAtEnd()
    }

    function clearConversation() {
        conversationData = []
    }

    ListView {
        id: conversation_view
        anchors.fill: parent
        anchors.margins: 10
        
        // Use the parent's data
        model: conversationData
        spacing: 6
        clip: true
        boundsBehavior: Flickable.StopAtBounds
        
        // Check if at end whenever content position changes
        onContentYChanged: {
            // Consider "at end" if within 100 pixels of the bottom
            conversationViewRoot.atEnd = (contentHeight - (contentY + height) < 100)
        }

        delegate: Column {
            width: conversation_view.width
            spacing: 2
            property string messageId: modelData.id || index

            // Timestamp and Speaker Row
            Row {
                width: parent.width
                spacing: 5

                // Time Stamp
                TextEdit {
                    text: modelData.timestamp
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
                    text: modelData.speaker + ":"
                    font.bold: true
                    font.italic: modelData.direction === "Other"
                    color: modelData.direction === "Other" ? conversationViewRoot.otherSpeakerColor : conversationViewRoot.userSpeakerColor
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
                    text: modelData.origin_text || ""
                    font.pixelSize: 13
                    font.italic: modelData.direction === "Other"
                    color: modelData.direction === "Other" ? conversationViewRoot.otherSpeakerColor : conversationViewRoot.userSpeakerColor
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
                    text: modelData.translated_text || ""
                    font.pixelSize: 13
                    font.italic: modelData.direction === "Other"
                    color: modelData.direction === "Other" ? conversationViewRoot.otherSpeakerColor : conversationViewRoot.userSpeakerColor
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
            if (count > 0 && conversationViewRoot.atEnd) {
                // Use a timer to delay the scroll to end to ensure data is fully loaded
                Qt.callLater(function() {
                    conversation_view.positionViewAtEnd()
                })
            }
        }
    }
    
    // Empty state (should be outside the ListView)
    Text {
        anchors.centerIn: parent
        text: "No conversation history"
        font.pixelSize: 16
        color: "#999"
        visible: conversationData.length === 0
    }
}
