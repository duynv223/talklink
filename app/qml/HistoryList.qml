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
    property var historyModel: ListModel {}

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
                    
                    // Duration
                    Text {
                        text: "Duration: " + model.duration
                        font.pixelSize: 13
                        color: "#666"
                    }
                    
                    Item { Layout.fillWidth: true }
                    
                    // Open button
                    Button {
                        text: "Open"
                        implicitWidth: 80
                        onClicked: {
                            // TODO: Open conversation
                            console.log("Open conversation:", model.id)
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
                
                // Speakers
                Flow {
                    width: parent.width
                    spacing: 6
                    
                    Repeater {
                        model: JSON.parse(model.speakers || "[]")
                        
                        Rectangle {
                            width: speakerText.width + 16
                            height: speakerText.height + 8
                            radius: height / 2
                            color: "#e0e0e0"
                            
                            Text {
                                id: speakerText
                                anchors.centerIn: parent
                                text: modelData
                                font.pixelSize: 12
                            }
                        }
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

    // Container cho các buttons
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
                id: clearHistoryButton
                iconSource: "../assets/conversation_action/clear-12.svg"
                onClicked: historyModel.clear()
                ToolTip.text: "Clear History"
                ToolTip.visible: hovered
                ToolTip.delay: 500
            }
        }
    }
    
    // Populate with sample data
    Component.onCompleted: {
        // Add sample history data
        addSampleData()
    }
    
    // Function to add sample data
    function addSampleData() {
        historyModel.clear()
        
        // Sample conversations
        historyModel.append({
            id: "conv1",
            date: "July 4, 2025 - 10:30 AM",
            duration: "15:32",
            preview: "Hello! How can I help you today? I'm interested in learning more about your products.",
            speakers: JSON.stringify(["You", "Customer", "Translated"])
        })
        
        historyModel.append({
            id: "conv2",
            date: "July 3, 2025 - 3:45 PM",
            duration: "8:15",
            preview: "I'd like to book a meeting for next week. What time works for you?",
            speakers: JSON.stringify(["You", "John", "Mary"])
        })
        
        historyModel.append({
            id: "conv3",
            date: "July 1, 2025 - 9:00 AM",
            duration: "22:47",
            preview: "Let's discuss the project timeline. We need to finalize the delivery dates.",
            speakers: JSON.stringify(["You", "Manager", "Team Lead"])
        })
    }
}
