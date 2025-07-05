import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: actionBar
    
    // Size properties
    height: 60
    width: buttonRow.width + 30
    z: 100
    
    // Customizable properties
    property bool showSummaryButton: true
    property bool showClearButton: true
    property bool showRenameButton: true
    property bool showNewButton: true
    
    // Signal declarations
    signal summaryClicked()
    signal clearClicked()
    signal renameClicked()
    signal newConversationClicked()
    
    // Default positioning - anchors to bottom right
    anchors.right: parent ? parent.right : undefined
    anchors.bottom: parent ? parent.bottom : undefined
    
    Row {
        id: buttonRow
        spacing: 10
        anchors.centerIn: parent
        
        IconButton {
            id: summaryConversationButton
            iconSource: "../assets/conversation_action/historical-sumary-svgrepo-com.svg"
            visible: showSummaryButton
            onClicked: actionBar.summaryClicked()
        }
        
        IconButton {
            id: clearConversationButton
            iconSource: "../assets/conversation_action/clear-12.svg"
            visible: showClearButton
            onClicked: actionBar.clearClicked()
        }
        
        IconButton {
            id: renameSpeakerButton
            iconSource: "../assets/conversation_action/rename-15.svg"
            visible: showRenameButton
            onClicked: actionBar.renameClicked()
        }
        
        IconButton {
            id: newConversationButton
            iconSource: "../assets/conversation_action/add-90.svg"
            visible: showNewButton
            onClicked: actionBar.newConversationClicked()
        }
    }
}
