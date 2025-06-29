import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Dialog {
    id: settingsDialog
    title: "Settings"
    modal: true
    standardButtons: Dialog.Ok
    width: 400
    height: 400
    x: (parent ? parent.width : Screen.width) / 2 - width / 2
    y: (parent ? parent.height : Screen.height) / 2 - height / 2
    z: 100
    property var model

    onVisibleChanged: {
        if (settingsDialog.visible && audioDeviceManager && audioDeviceManager.refresh)
            audioDeviceManager.refresh();
    }

    contentItem: ColumnLayout {
        spacing: 12
        anchors.fill: parent
        anchors.margins: 16

        Text {
            text: "Mixer"
            font.pixelSize: 13
            Layout.fillWidth: true
            horizontalAlignment: Text.AlignLeft
            padding: 4
            topPadding: 8
        }

        // Mixer rectangle
        Rectangle {
            Layout.fillWidth: true
            color: "#f0f0f0"
            radius: 8
            border.color: "#e0e0e0"
            border.width: 1
            height: 110

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 12
                spacing: 10

                RowLayout {
                    spacing: 8
                    Label { text: "Original"; Layout.preferredWidth: 90 }
                    Slider {
                        id: originalVolumeSlider
                        from: 0; to: 50
                        value: settingModel.get("conference.volume.original") * 50
                        stepSize: 1
                        Layout.fillWidth: true
                        onValueChanged: {
                            if (settingModel.set)
                                settingModel.set("conference.volume.original", value / 50)
                        }
                    }
                    Label { text: Math.round(originalVolumeSlider.value).toString(); Layout.preferredWidth: 30 }
                }
                RowLayout {
                    spacing: 8
                    Label { text: "Tranlated"; Layout.preferredWidth: 90 }
                    Slider {
                        id: ttsVolumeSlider
                        from: 0; to: 50
                        value: settingModel.get("conference.volume.translated") * 50
                        stepSize: 1
                        Layout.fillWidth: true
                        onValueChanged: {
                            if (settingModel.set)
                                settingModel.set("conference.volume.translated", value / 50)
                        }
                    }
                    Label { text: Math.round(ttsVolumeSlider.value).toString(); Layout.preferredWidth: 30 }
                }
            }
        }

        Text {
            text: "Microphone"
            font.pixelSize: 13
            Layout.fillWidth: true
            horizontalAlignment: Text.AlignLeft
        }
        ModernComboBox {
            id: inputDeviceCombo
            Layout.fillWidth: true
            model: (audioDeviceManager.inputDevices && audioDeviceManager.inputDevices.length > 0) ? audioDeviceManager.inputDevices : [ { name: "Default Input" }, { name: "Mic 1" }, { name: "Mic 2" } ]
            textRole: "name"
            currentIndex: {
                let idx = 0;
                if (settingModel.get && settingModel.get("conference.input_device")) {
                    let arr = (audioDeviceManager.inputDevices && audioDeviceManager.inputDevices.length > 0) ? audioDeviceManager.inputDevices : [ { name: "Default Input" }, { name: "Mic 1" }, { name: "Mic 2" } ];
                    for (let i = 0; i < arr.length; ++i) {
                        if (arr[i].name === settingModel.get("conference.input_device")) {
                            idx = i; break;
                        }
                    }
                }
                return idx;
            }
            onCurrentIndexChanged: {
                let arr = (audioDeviceManager.inputDevices && audioDeviceManager.inputDevices.length > 0) ? audioDeviceManager.inputDevices : [ { name: "Default Input" }, { name: "Mic 1" }, { name: "Mic 2" } ];
                if (settingModel.set)
                    settingModel.set("conference.input_device", arr[currentIndex].name)
            }
        }
        Text {
            text: "Speaker"
            font.pixelSize: 13
            Layout.fillWidth: true
            horizontalAlignment: Text.AlignLeft
        }
        ModernComboBox {
            id: outputDeviceCombo
            Layout.fillWidth: true
            model: (audioDeviceManager.outputDevices && audioDeviceManager.outputDevices.length > 0) ? audioDeviceManager.outputDevices : [ { name: "Default Output" }, { name: "Speaker 1" }, { name: "Speaker 2" } ]
            textRole: "name"
            currentIndex: {
                let idx = 0;
                if (settingModel.get && settingModel.get("conference.output_device")) {
                    let arr = (audioDeviceManager.outputDevices && audioDeviceManager.outputDevices.length > 0) ? audioDeviceManager.outputDevices : [ { name: "Default Output" }, { name: "Speaker 1" }, { name: "Speaker 2" } ];
                    for (let i = 0; i < arr.length; ++i) {
                        if (arr[i].name === settingModel.get("conference.output_device")) {
                            idx = i; break;
                        }
                    }
                }
                return idx;
            }
            onCurrentIndexChanged: {
                let arr = (audioDeviceManager.outputDevices && audioDeviceManager.outputDevices.length > 0) ? audioDeviceManager.outputDevices : [ { name: "Default Output" }, { name: "Speaker 1" }, { name: "Speaker 2" } ];
                if (settingModel.set)
                    settingModel.set("conference.output_device", arr[currentIndex].name)
            }
        }
        Item {
            Layout.fillHeight: true
        }
    }
}
