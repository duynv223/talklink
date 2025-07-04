import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "."

Rectangle {
    id: renameSpeakerSidebar
    width: 270
    anchors.top: parent.top
    anchors.bottom: parent.bottom
    anchors.right: parent.right
    
    property bool isVisible: false
    property var speakerModel: []
    signal speakerRenamed(string speakerId, string newName)
    signal hideSidebar()
    
    anchors.rightMargin: isVisible ? 0 : -width
    color: "#ffffff"
    border.color: "#e0e0e0"
    border.width: 1
    z: 50

    // Animation
    Behavior on anchors.rightMargin {
        NumberAnimation { 
            duration: 250
            easing.type: Easing.OutQuad
        }
    }
    
    // Header
    Rectangle {
        id: sidebarHeader
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: 50
        color: "#f0f0f0"
        
        Text {
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: parent.left
            anchors.leftMargin: 15
            text: "Speaker Management"
            font.pixelSize: 16
            font.bold: true
            color: "#333333"
        }
        
        IconButton {
            anchors.verticalCenter: parent.verticalCenter
            anchors.right: parent.right
            anchors.rightMargin: 10
            iconSource: "../assets/conversation_action/clear-27.svg"
            onClicked: {
                isVisible = false
                hideSidebar()
            }
        }
    }
    
    // Speaker List
    ListView {
        id: speakerListView
        anchors.top: sidebarHeader.bottom
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.margins: 10
        spacing: 10
        clip: true
        
        model: speakerModel
        
        ScrollBar.vertical: ScrollBar {
            active: true
            policy: ScrollBar.AsNeeded
        }
        
        boundsBehavior: Flickable.StopAtBounds
        
        delegate: Rectangle {
            width: parent ? parent.width : 230
            height: 50
            color: "#f8f8f8"
            radius: 4
            border.color: "#e0e0e0"
            border.width: 1
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: 8
                spacing: 8
                
                Text {
                    text: "ID: " + modelData.speaker_Id
                    font.pixelSize: 12
                    color: "#666666"
                    Layout.preferredWidth: 80
                    elide: Text.ElideRight
                }
                
                // New name input
                TextField {
                    id: newNameField
                    text: modelData.speaker_Name
                    placeholderText: "Enter new name"
                    font.pixelSize: 13
                    height: 28
                    Layout.fillWidth: true
                }

                IconButton {
                    id: summaryConversationButton
                    iconSource: "../assets/conversation_action/rename-15.svg"
                    onClicked: {
                        if (newNameField.text.trim() !== "") {
                            speakerRenamed(modelData.speaker_Id, newNameField.text)
                        }
                    }
                }
            }
        }
        
        Text {
            anchors.centerIn: parent
            text: "No speakers available"
            color: "#999999"
            font.pixelSize: 14
            visible: speakerModel.length === 0
        }
    }
}