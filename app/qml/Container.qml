import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: container
    property int currentIndex: 0
    signal currentIndexChanged(int idx)
    width: 800
    height: 600

    RowLayout {
        anchors.fill: parent

        SidebarNavigation {
            id: sidebar
            width: 150
            Layout.fillHeight: true
            currentIndex: container.currentIndex
            onCurrentIndexChanged: container.currentIndex = currentIndex
        }

        Item {
            id: contentItem
            Layout.fillWidth: true
            Layout.fillHeight: true
        }
    }

    default property alias content: contentItem.data
}
