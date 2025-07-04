import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: renameSpeakerSidebar
    width: 250
    anchors.top: parent.top
    anchors.bottom: parent.bottom
    anchors.right: parent.right
    
    property bool isVisible: false
    property var speakerModel: ListModel {}
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
        color: "#f5f5f5"
        
        Text {
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: parent.left
            anchors.leftMargin: 15
            text: "Rename Speakers"
            font.pixelSize: 16
            font.bold: true
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
        anchors.top: sidebarHeader.bottom
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.margins: 10
        spacing: 10
        clip: true
        
        model: speakerModel
        
        delegate: Rectangle {
            width: parent ? parent.width : 230
            height: 80
            color: "#f9f9f9"
            radius: 5
            border.color: "#e0e0e0"
            border.width: 1
            
            Column {
                anchors.fill: parent
                anchors.margins: 10
                spacing: 5
                
                Text {
                    text: "Current name: " + speakerName
                    font.pixelSize: 13
                }
                
                TextField {
                    id: newNameField
                    placeholderText: "New name"
                    width: parent.width
                }
                
                Button {
                    text: "Rename"
                    width: parent.width
                    onClicked: {
                        if (newNameField.text.trim() !== "") {
                            speakerRenamed(speakerId, newNameField.text)
                            newNameField.text = ""
                        }
                    }
                }
            }
        }
    }
}