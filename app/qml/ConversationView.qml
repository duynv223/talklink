import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

ListView {
    id: conversation_view
    
    // Customizable properties
    property var conversationData: []
    property color otherSpeakerColor: "#888"
    property color userSpeakerColor: "#2e7d32"
    
    // Default settings
    Layout.fillHeight: true
    model: conversationData
    spacing: 6
    clip: true
    boundsBehavior: Flickable.StopAtBounds

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
                color: modelData.direction === "Other" ? conversation_view.otherSpeakerColor : conversation_view.userSpeakerColor
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
                color: modelData.direction === "Other" ? conversation_view.otherSpeakerColor : conversation_view.userSpeakerColor
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
                color: modelData.direction === "Other" ? conversation_view.otherSpeakerColor : conversation_view.userSpeakerColor
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
            conversation_view.positionViewAtEnd()
    }

    // Add methods that can be called from parent
    function scrollToEnd() {
        conversation_view.positionViewAtEnd()
    }

    function clearConversation() {
        conversationData = []
    }
}
