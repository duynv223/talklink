import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Dialog {
    id: settingsDialog
    title: "Settings"
    modal: true
    standardButtons: Dialog.Ok
    width: 400
    height: 300
    x: (parent ? parent.width : Screen.width) / 2 - width / 2
    y: (parent ? parent.height : Screen.height) / 2 - height / 2
    z: 100
    property var model

    Component.onCompleted: {
        console.log("[SettingsDialog] model:", model)
    }

    contentItem: Column {
        spacing: 12
        padding: 16

        Text {
            text: "Mixer"
            font.pixelSize: 13
            anchors.left: parent.left
            width: parent.width
            horizontalAlignment: Text.AlignLeft
        }

        // Mixer rectangle
        Rectangle {
            width: parent.width
            color: "#f0f0f0"
            radius: 8
            border.color: "#e0e0e0"
            border.width: 1
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.margins: 0
            height: 110

            Column {
                anchors.fill: parent
                anchors.margins: 12
                spacing: 10

                Row {
                    spacing: 8
                    Label { text: "Original"; width: 110 }
                    Slider {
                        id: originalVolumeSlider
                        from: 0; to: 50
                        value: model.get("conference.volume.original") * 50
                        stepSize: 1
                        width: 140
                        onValueChanged: {
                            if (model.set)
                                model.set("conference.volume.original", value / 50)
                        }
                    }
                    Label { text: Math.round(originalVolumeSlider.value).toString(); width: 50 }
                }
                Row {
                    spacing: 8
                    Label { text: "Tranlated"; width: 110 }
                    Slider {
                        id: ttsVolumeSlider
                        from: 0; to: 50
                        value: model.get("conference.volume.translated") * 50
                        stepSize: 1
                        width: 140
                        onValueChanged: {
                            if (model.set)
                                model.set("conference.volume.translated", value / 50)
                        }
                    }
                    Label { text: Math.round(ttsVolumeSlider.value).toString(); width: 30 }
                }
            }
        }
    }
}
