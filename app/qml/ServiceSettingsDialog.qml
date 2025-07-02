import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Dialog {
    id: dialog
    property string module: ""
    title: module + " Settings"
    standardButtons: Dialog.Ok | Dialog.Cancel
    modal: true
    focus: true
    width: 400
    height: 320
    x: (parent ? parent.width : Screen.width) / 2 - width / 2
    y: (parent ? parent.height : Screen.height) / 2 - height / 2

    property string selectedService: ""
    property var fields: []

    function updateFields() {
        selectedService = serviceSettingModel.getSelectedService(module)
        fields = serviceSettingModel.getServiceFields(module, selectedService)
    }

    onModuleChanged: updateFields()

    Component.onCompleted: {
        serviceSettingModel.serviceChanged.connect(updateFields)
        serviceSettingModel.fieldChanged.connect(updateFields)
        updateFields()
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 12
        
        Item {
            visible: !fields || fields.length === 0
            Layout.fillWidth: true
            Text {
                text: "No settings available for this service."
                color: "#888"
                font.italic: true
                font.pixelSize: 14
                anchors.horizontalCenter: parent.horizontalCenter
            }
        }
        
        Repeater {
            model: fields
            visible: fields && fields.length > 0
            delegate: RowLayout {
                spacing: 8
                Text { text: modelData.label || modelData.key; Layout.preferredWidth: 120 }
                Loader {
                    property string fieldType: modelData.type || "string"
                    sourceComponent: fieldType === "number" ? numberField : textField
                    property string fieldKey: modelData.key
                    property string fieldValue: serviceSettingModel.getFieldValue(module, fieldKey)
                    onLoaded: {
                        if (item) {
                            item.module = module
                            item.fieldKey = fieldKey
                            item.fieldValue = fieldValue
                        }
                    }
                }
                Component {
                    id: textField
                    TextField {
                        Layout.preferredWidth: 180
                        property string module
                        property string fieldKey
                        property string fieldValue
                        text: fieldValue
                        onEditingFinished: serviceSettingModel.setFieldValue(module, fieldKey, text)
                    }
                }
                Component {
                    id: numberField
                    SpinBox {
                        Layout.preferredWidth: 120
                        property string module
                        property string fieldKey
                        property string fieldValue
                        value: parseInt(fieldValue)
                        from: modelData.min !== undefined ? modelData.min : -999999
                        to: modelData.max !== undefined ? modelData.max : 999999
                        stepSize: modelData.step !== undefined ? modelData.step : 1
                        onValueChanged: serviceSettingModel.setFieldValue(module, fieldKey, value.toString())
                    }
                }
            }
        }
        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true
        }
    }
}
