import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "."

Rectangle {
    width: parent ? parent.width : 400
    height: 120
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
                    let lang = settingModel.get("conference.other_lang");
                    for (var i = 0; i < model.length; ++i)
                        if (model[i].code === lang)
                            return i;
                    return 0;
                }
                onCurrentIndexChanged: {
                    if (settingModel.set)
                        settingModel.set("conference.other_lang", model[currentIndex].code)
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
                    let lang = settingModel.get("conference.your_lang");
                    for (var i = 0; i < model.length; ++i)
                        if (model[i].code === lang)
                            return i;
                    return 1;
                }
                onCurrentIndexChanged: {
                    if (settingModel.set)
                        settingModel.set("conference.your_lang", model[currentIndex].code)
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

        // Split line
        Rectangle {
            width: parent ? parent.width : 400
            height: 1
            color: "#e0e0e0"
            Layout.fillWidth: true
            Layout.topMargin: 8
            Layout.bottomMargin: 8
        }

        // Audio control panel
        RowLayout {
            Layout.fillWidth: true
            spacing: 16
            
            RowLayout {
                spacing: 6
                Label { text: "Other"; font.bold: true; color: "#333" }
                ToggleButton {
                    iconSource: "../assets/asr.svg";
                    width: 28;
                    height: 28
                    active: true
                    onClicked: {
                        if (pipeline.toggleASR)
                            pipeline.toggleASR()
                    }
                }

                ToggleButton {
                    iconSource: "../assets/tts.svg";
                    width: 28;
                    height: 28
                    active: true
                    onClicked: {
                        if (pipeline.toggleOtherTTS)
                            pipeline.toggleOtherTTS()
                    }
                }
            }

            RowLayout {
                spacing: 6
                Label { text: "You"; font.bold: true; color: "#333" }
                ToggleButton {
                    iconSource: "../assets/asr.svg";
                    width: 28;
                    height: 28
                    active: true
                    onClicked: {
                        if (pipeline.toggleYourASR)
                            pipeline.toggleYourASR()
                    }
                }

                ToggleButton {
                    iconSource: "../assets/tts.svg";
                    width: 28;
                    height: 28
                    active: true
                    onClicked: {
                        if (pipeline.toggleYourTTS)
                            pipeline.toggleYourTTS()
                    }
                }
            }

            Item { Layout.fillWidth: true }

            IconButton {
                id: micButton
                width: 40
                height: 32
                property bool micOn: true
                iconSource: micOn ? "../assets/mic-on.svg" : "../assets/mic-off.svg"
                onClicked: micOn = !micOn
            }
            IconButton {
                id: speakerButton
                width: 40
                height: 32
                property bool micOn: true
                iconSource: micOn ? "../assets/sound-on.svg" : "../assets/sound-mute.svg"
                onClicked: micOn = !micOn
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
                                value: settingModel.get("conference.volume.original") * 50
                                stepSize: 1
                                width: 140
                                onValueChanged: {
                                    if (settingModel.set)
                                        settingModel.set("conference.volume.original", value / 50)
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
                                value: settingModel.get("conference.volume.translated") * 50
                                stepSize: 1
                                width: 140
                                onValueChanged: {
                                    if (settingModel.set)
                                        settingModel.set("conference.volume.translated", value / 50)
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