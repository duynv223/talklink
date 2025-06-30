import QtQuick 2.15
import QtQuick.Controls 2.15

ComboBox {
    id: modernCombo
    background: Rectangle {
        color: modernCombo.enabled ? "#fff" : "#f0f0f0"
        border.color: modernCombo.activeFocus ? "#448aff" : "#cccccc"
        border.width: 1
        radius: 8
    }
    contentItem: Text {
        text: modernCombo.displayText
        color: modernCombo.enabled ? "#222" : "#aaa"
        verticalAlignment: Text.AlignVCenter
        leftPadding: 10
        rightPadding: 10
        font.pixelSize: 15
        width: modernCombo.width - 20
        elide: Text.ElideRight
        maximumLineCount: 1
        clip: true
    }
    indicator: Rectangle {
        width: 20
        height: 20
        color: "transparent"
        border.width: 0
        anchors.verticalCenter: parent.verticalCenter
        anchors.right: parent.right
        anchors.rightMargin: 8
        Image {
            anchors.centerIn: parent
            source: "../assets/arrow-down.svg"
            width: 14
            height: 14
            fillMode: Image.PreserveAspectFit
        }
    }
    popup: Popup {
        y: modernCombo.height
        width: modernCombo.width
        implicitHeight: Math.max(contentItem.implicitHeight, delegateModel.count * 36)
        background: Rectangle {
            color: "#fff"
            border.color: "#cccccc"
            border.width: 1
            radius: 8
        }
        contentItem: ListView {
            clip: true
            implicitHeight: delegateModel.count * 36
            model: modernCombo.delegateModel
            delegate: modernCombo.delegate
            currentIndex: modernCombo.highlightedIndex
        }
    }
}
