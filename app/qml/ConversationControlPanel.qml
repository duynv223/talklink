import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "."

Rectangle {
    width: parent ? parent.width : 400
    height: 80
    color: "#f8f8f8"
    radius: 8
    border.color: "#e0e0e0"
    border.width: 1

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 6

        RowLayout {
            Layout.fillWidth: true
            spacing: 12

            ModernComboBox {
                id: srcLangCombo
                Layout.preferredWidth: 120
                model: [
                    { label: "English", code: "en" },
                    { label: "Vietnamese", code: "vi" },
                    { label: "Japanese", code: "ja" }
                ]
                textRole: "label"
                currentIndex: {
                    for (var i = 0; i < model.length; ++i)
                        if (model[i].code === pipeline.sourceLanguage)
                            return i;
                    return 0;
                }
                onCurrentIndexChanged: {
                    if (pipeline.setOtherLanguage)
                        pipeline.setOtherLanguage(model[currentIndex].code)
                }
            }

            Image {
                source: "../assets/compare.svg"
                width: 20
                height: 20
                fillMode: Image.PreserveAspectFit
                sourceSize.width: 20
                sourceSize.height: 20
                Layout.alignment: Qt.AlignVCenter
            }

            ModernComboBox {
                id: dstLangCombo
                Layout.preferredWidth: 120
                model: [
                    { label: "English", code: "en" },
                    { label: "Vietnamese", code: "vi" },
                    { label: "Japanese", code: "ja" }
                ]
                textRole: "label"
                currentIndex: {
                    for (var i = 0; i < model.length; ++i)
                        if (model[i].code === pipeline.targetLanguage)
                            return i;
                    return 1;
                }
                onCurrentIndexChanged: {
                    if (pipeline.setYourLanguage)
                        pipeline.setYourLanguage(model[currentIndex].code)
                }
            }

            Item { Layout.fillWidth: true }

            IconButton {
                id: runButton
                width: 120
                height: 32
                property string appState: pipeline.appState

                label: appState === "Stopped" ? "Start"
                    : appState === "Starting" ? "Starting..."
                    : appState === "Running" ? "Stop"
                    : appState === "Stopping" ? "Stopping..."
                    : ""

                iconSource: appState === "Stopped" ? "../assets/run.svg"
                    : appState === "Starting" ? "../assets/hourglass.svg"
                    : appState === "Running" ? "../assets/stop.svg"
                    : appState === "Stopping" ? "../assets/hourglass.svg"
                    : ""

                allowSpin: appState === "Starting" || appState === "Stopping"
                spinning: appState === "Starting" || appState === "Stopping"
                blinking: appState === "Starting"

                backgroundColor: appState === "Stopped" ? "#E8F5E9"
                    : appState === "Starting" ? "#E3F2FD"
                    : appState === "Running" ? "#FFEBEE"
                    : appState === "Stopping" ? "#FFF8E1"
                    : "#F5F5F5"

                onClicked: {
                    if (appState === "Stopped") {
                        pipeline.start()
                    } else if (appState === "Running") {
                        pipeline.stop()
                    }
                }
            }

            IconButton {
                id: settingsButton
                label: "Settings"
                iconSource: "../assets/settings.svg"
                onClicked: settingsDialog.open()
            }
        }

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
                                value: 40
                                stepSize: 1
                                width: 140
                                onValueChanged: {
                                    if (pipeline.setOriginalVolume)
                                        pipeline.setOriginalVolume(value / 50)
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
                                value: 40
                                stepSize: 1
                                width: 140
                                onValueChanged: {
                                    if (pipeline.setTranslatedVolume)
                                        pipeline.setTranslatedVolume(value / 100)
                                }
                            }
                            Label { text: Math.round(ttsVolumeSlider.value).toString(); width: 30 }
                        }
                    }
                }
            }
        }
    }
}