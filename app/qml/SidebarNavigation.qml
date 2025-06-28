import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: sidebar
    property int currentIndex: 0
    color: "#f0f0f0"

    Item {
        anchors.fill: parent
        anchors.margins: 20

        ColumnLayout {
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter
            spacing: 10

            SidebarNavButton {
                iconSource: "../assets/mic.svg"
                label: "Conversation"
                active: sidebar.currentIndex === 0
                onClicked: sidebar.currentIndex = 0
            }

            SidebarNavButton {
                iconSource: "../assets/history.svg"
                label: "History"
                active: sidebar.currentIndex === 1
                onClicked: sidebar.currentIndex = 1
            }

            SidebarNavButton {
                iconSource: "../assets/settings.svg"
                label: "Settings"
                active: sidebar.currentIndex === 2
                onClicked: sidebar.currentIndex = 2
            }
        }
    }
}