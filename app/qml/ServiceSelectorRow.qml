import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

RowLayout {
    property string module: ""
    property string title: ""
    property alias comboBox: combo
    signal settingsClicked(string module)

    spacing: 8
    Text {
        text: title
        font.pixelSize: 14
        Layout.alignment: Qt.AlignVCenter
        Layout.preferredWidth: 140
    }
    ComboBox {
        id: combo
        Layout.preferredWidth: 220
        Layout.alignment: Qt.AlignVCenter
        model: serviceSettingModel ? serviceSettingModel.getServiceList(module) : []
        textRole: "name"
        valueRole: "id"
        currentIndex: serviceSettingModel ? serviceSettingModel.getServiceList(module)
            .findIndex(function(s) {
                return s.id === (serviceSettingModel ? serviceSettingModel.getSelectedService(module) : "")
            }) : -1
        onCurrentIndexChanged: {
            if (serviceSettingModel) {
                let newId = serviceSettingModel.getServiceList(module)[currentIndex].id
                serviceSettingModel.setSelectedService(module, newId)
            }
        }
    }
    Button {
        text: "Settings"
        Layout.alignment: Qt.AlignVCenter
        onClicked: settingsClicked(module)
    }
}
