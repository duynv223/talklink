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

        Rectangle { // ngăn cách
            width: 1
            color: "#e0e0e0"
            Layout.fillHeight: true
        }

        ListView {
            id: conversation_view
            Layout.preferredWidth: parent ? parent.width * 0.7 : 500
            Layout.fillHeight: true
            Layout.margins: 10
            model: conversation_data
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
                        color: "#888"
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
                        text: modelData.translated_text || ""
                        font.pixelSize: 13
                        font.italic: modelData.direction === "Other"
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
                    conversation_view.positionViewAtEnd()
            }
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
                onClicked:  {
                    summaryPopup.open()
                    summaryPopup.loading = true
                    historyModel.summarizeConversation()
                }
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
            historyModel.updateSpeakerName(speakerId, newName)
        }
        onHideSidebar: {
            sidebarVisible = false
        }
    }

    Component.onCompleted: {
        initializedSidebar = true
        
        // Lấy dữ liệu conversation khi mở view
        if (historyModel && historyModel.getConversationData) {
            conversation_data = historyModel.getConversationData()
        }
    }

    Connections {
        target: historyModel
        function onUniqueSpeakersChanged() {
            if (sidebarVisible) {
                speakerSidebar.speakerModel = historyModel.getUniqueSpeakerMaps()
            }
        }

        function onConversationDataChanged() {
            historyList.conversation_data = historyModel.getConversationData()
        }

        function onSummaryReady(text) {
            summaryPopup.loading = false
            summaryPopup.result = text
        }

        function onSummaryError(err) {
            summaryPopup.loading = false
            summaryPopup.result = "Error: " + err
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

    Popup {
        id: summaryPopup
        modal: true
        focus: true
        width: parent ? parent.width * 0.75 : 700
        height: parent ? parent.height * 0.6 : 500
        padding: 20
        closePolicy: Popup.CloseOnEscape
        anchors.centerIn: parent

        // Custom properties
        property bool loading: false
        property string result: ""

        background: Rectangle {
            color: "#ffffff"
            radius: 10
            border.color: "#cccccc"
        }

        ColumnLayout {
            anchors.fill: parent
            spacing: 12

            // Title
            Label {
                text: "Summary Conversation"
                font.pixelSize: 18
                font.bold: true
                Layout.alignment: Qt.AlignHCenter
                horizontalAlignment: Text.AlignHCenter 
            }

            // Loading indicator
            Loader {
                active: summaryPopup.loading
                sourceComponent: busyIndicatorComponent
                Layout.alignment: Qt.AlignHCenter
                visible: summaryPopup.loading
            }

            // Summary text
            ScrollView {
                visible: !summaryPopup.loading
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true
                Column {
                    width: summaryPopup.width - 40
                    spacing: 10

                    TextEdit {
                        text: summaryPopup.result
                        wrapMode: TextEdit.Wrap
                        font.pixelSize: 14
                        color: "#333"
                        readOnly: true
                        selectByMouse: true
                        width: parent.width
                    }
                }
            }

            // Button bar
            RowLayout {
                Layout.alignment: Qt.AlignRight
                Layout.fillWidth: true

                Button {
                    text: "Đóng"
                    onClicked: summaryPopup.close()
                }
            }
        }

        // BusyIndicator component
        Component {
            id: busyIndicatorComponent
            Item {
                width: 40
                height: 40
                BusyIndicator {
                    running: true
                    anchors.centerIn: parent
                }
            }
        }
    }
}
