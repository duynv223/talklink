import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

ApplicationWindow {
    id: app
    width: 800
    height: 600
    visible: true
    title: "Voice Translator"

    RowLayout {
        anchors.fill: parent

        // Sử dụng component SidebarNavigation thay cho Rectangle sidebar
        SidebarNavigation {
            id: sidebar
            width: 110
            color: "#e8e8e8"
            Layout.fillHeight: true
            currentIndex: stack.currentIndex
            onCurrentIndexChanged: stack.currentIndex = currentIndex
        }

        StackLayout {
            id: stack   
            Layout.fillWidth: true
            Layout.fillHeight: true

            // Tab: Conversation
            Item {
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins:10
                    spacing: 10
                    ConversationControlPanel { Layout.fillWidth: true }
                    ConversationList { 
                        id: conversationList
                        Layout.fillWidth: true
                        Layout.fillHeight: true 
                    }
                    ConversationStatusBar {
                        id: conversationStatusBar
                        Layout.alignment: Qt.AlignRight | Qt.AlignBottom
                        Layout.fillWidth: true
                    }
                }
            }

            // Tab: History
            Item {
                ColumnLayout {
                    anchors.fill: parent
                    spacing: 10
                    Text { text: "History (T.B.D)"; font.pixelSize: 24 }
                }
            }

            // Tab: Settings
            Item {
                ColumnLayout {
                    anchors.fill: parent
                    spacing: 10
                    Text { text: "Settings (T.B.D)"; font.pixelSize: 24 }
                }
            }
        }
    }
}