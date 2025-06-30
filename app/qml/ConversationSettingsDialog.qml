import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Dialog {
    id: settingsDialog
    title: "Settings"
    modal: true
    standardButtons: Dialog.Ok
    width: 400
    height: 500
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
            model: audioDeviceManager ? audioDeviceManager.inputDevices : []
            textRole: "name"
            property int lastIndex: currentIndex
            currentIndex: {
                let idx = 0;
                if (settingModel.get && settingModel.get("conference.input_device")) {
                    let arr = audioDeviceManager ? audioDeviceManager.inputDevices : [];
                    for (let i = 0; i < arr.length; ++i) {
                        if (arr[i].name === settingModel.get("conference.input_device")) {
                            idx = i; break;
                        }
                    }
                }
                return idx;
            }
            onCurrentIndexChanged: {
                let arr = audioDeviceManager ? audioDeviceManager.inputDevices : [];
                if (settingModel.set && arr.length > 0)
                    settingModel.set("conference.input_device", arr[currentIndex].name)
            }
            Connections {
                target: audioDeviceManager
                function onDevicesChanged() {
                    inputDeviceCombo.forceActiveFocus();
                    inputDeviceCombo.currentIndex = inputDeviceCombo.currentIndex;
                }
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
            model: audioDeviceManager ? audioDeviceManager.outputDevices : []
            textRole: "name"
            property int lastIndex: currentIndex
            currentIndex: {
                let idx = 0;
                if (settingModel.get && settingModel.get("conference.output_device")) {
                    let arr = audioDeviceManager ? audioDeviceManager.outputDevices : [];
                    for (let i = 0; i < arr.length; ++i) {
                        if (arr[i].name === settingModel.get("conference.output_device")) {
                            idx = i; break;
                        }
                    }
                }
                return idx;
            }
            onCurrentIndexChanged: {
                let arr = audioDeviceManager ? audioDeviceManager.outputDevices : [];
                if (settingModel.set && arr.length > 0)
                    settingModel.set("conference.output_device", arr[currentIndex].name)
            }
            Connections {
                target: audioDeviceManager
                function onDevicesChanged() {
                    outputDeviceCombo.forceActiveFocus();
                    outputDeviceCombo.currentIndex = outputDeviceCombo.currentIndex;
                }
            }
        }

        Text {
            text: "TTS Speed"
            font.pixelSize: 13
            Layout.fillWidth: true
            horizontalAlignment: Text.AlignLeft
            padding: 4
            topPadding: 8
        }
        Rectangle {
            Layout.fillWidth: true
            color: "#f0f0f0"
            radius: 8
            border.color: "#e0e0e0"
            border.width: 1
            height: 80
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 12
                spacing: 10
                RowLayout {
                    spacing: 8
                    Label { text: "Other"; Layout.preferredWidth: 90 }
                    Slider {
                        id: ttsSpeedOtherSlider
                        from: 0.5; to: 2.0
                        value: settingModel.get("conference.downstream.tts_speed") || 1.0
                        stepSize: 0.1
                        Layout.fillWidth: true
                        onValueChanged: {
                            if (settingModel.set)
                                settingModel.set("conference.downstream.tts_speed", value)
                        }
                    }
                    Label { text: ttsSpeedOtherSlider.value.toFixed(1) + "x"; Layout.preferredWidth: 40 }
                }
                RowLayout {
                    spacing: 8
                    Label { text: "You"; Layout.preferredWidth: 90 }
                    Slider {
                        id: ttsSpeedYouSlider
                        from: 0.5; to: 2.0
                        value: settingModel.get("conference.upstream.tts_speed") || 1.0
                        stepSize: 0.1
                        Layout.fillWidth: true
                        onValueChanged: {
                            if (settingModel.set)
                                settingModel.set("conference.upstream.tts_speed", value)
                        }
                    }
                    Label { text: ttsSpeedYouSlider.value.toFixed(1) + "x"; Layout.preferredWidth: 40 }
                }
            }
        }

        Item {
            Layout.fillHeight: true
        }
    }
}
