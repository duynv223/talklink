import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: indicator
    property real value: 0.0
    property color color: "#4caf50"
    property int barCount: 5
    property real maxValue: 0.3
    property int barSpacing: 2
    width: 30
    height: 30

    Column {
        anchors.fill: parent
        anchors.margins: 0
        spacing: indicator.barSpacing
        Repeater {
            model: indicator.barCount
            Rectangle {
                width: indicator.width
                height: (indicator.height - (indicator.barCount-1)*indicator.barSpacing) / indicator.barCount
                radius: 2
                color: indicator.color
                opacity: (barCount - index - 1) < Math.round(Math.min(indicator.value/indicator.maxValue, 1.0) * indicator.barCount) ? 1 : 0.2
                anchors.horizontalCenter: parent.horizontalCenter
            }
        }
    }
}
