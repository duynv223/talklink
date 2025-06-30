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
                    id: otherAsrEnable
                    iconSource: "../assets/asr.svg";
                    width: 28;
                    height: 28
                    active: settingModel.get("conference.downstream.asr_enable")
                    onClicked: {
                        if (settingModel.set)  {
                            var next = active ? false : true
                            settingModel.set("conference.downstream.asr_enable", next)
                        }
                    }
                    Connections {
                        target: settingModel
                        function onValueChanged(path, value) {
                            if (path === "conference.downstream.asr_enable") {
                                otherAsrEnable.active = value
                            }
                        }
                    }
                }

                ToggleButton {
                    id: otherTtsEnable
                    iconSource: "../assets/tts.svg";
                    width: 28;
                    height: 28
                    active: settingModel.get("conference.downstream.tts_enable")
                    onClicked: {
                        if (settingModel.set)  {
                            var next = active ? false : true
                            settingModel.set("conference.downstream.tts_enable", next)
                        }
                    }
                    Connections {
                        target: settingModel
                        function onValueChanged(path, value) {
                            if (path === "conference.downstream.tts_enable") {
                                otherTtsEnable.active = value
                            }
                        }
                    }
                }
            }

            RowLayout {
                spacing: 6
                Label { text: "You"; font.bold: true; color: "#333" }
                ToggleButton {
                    id: youAsrEnable
                    iconSource: "../assets/asr.svg";
                    width: 28;
                    height: 28
                    active: settingModel.get("conference.upstream.asr_enable")
                    onClicked: {
                        if (settingModel.set)  {
                            var next = active ? false : true
                            settingModel.set("conference.upstream.asr_enable", next)
                        }
                    }
                    Connections {
                        target: settingModel
                        function onValueChanged(path, value) {
                            if (path === "conference.upstream.asr_enable") {
                                youAsrEnable.active = value
                            }
                        }
                    }
                }

                ToggleButton {
                    id: youTtsEnable
                    iconSource: "../assets/tts.svg";
                    width: 28;
                    height: 28
                    active: settingModel.get("conference.upstream.tts_enable")
                    onClicked: {
                        if (settingModel.set)  {
                            var next = active ? false : true
                            settingModel.set("conference.upstream.tts_enable", next)
                        }
                    }
                    Connections {
                        target: settingModel
                        function onValueChanged(path, value) {
                            if (path === "conference.upstream.tts_enable") {
                                youTtsEnable.active = value
                            }
                        }
                    }
                }
            }

            Item { Layout.fillWidth: true }

            IconButton {
                id: micButton
                width: 40
                height: 32
                property bool micOn: !settingModel.get("conference.input_mute")
                iconSource: micOn ? "../assets/mic-on.svg" : "../assets/mic-off.svg"
                onClicked: {
                    if (settingModel.set) {
                        settingModel.set("conference.input_mute", micOn)
                    }
                }
                Connections {
                    target: settingModel
                    function onValueChanged(path, value) {
                        if (path === "conference.input_mute") {
                            micButton.micOn = !value
                        }
                    }
                }
            }
            IconButton {
                id: speakerButton
                width: 40
                height: 32
                property bool speakerOn: !settingModel.get("conference.output_mute")
                iconSource: speakerOn ? "../assets/sound-on.svg" : "../assets/sound-mute.svg"
                onClicked: {
                    if (settingModel.set) {
                        settingModel.set("conference.output_mute", speakerOn)
                    }
                }
                Connections {
                    target: settingModel
                    function onValueChanged(path, value) {
                        if (path === "conference.output_mute") {
                            speakerButton.speakerOn = !value
                        }
                    }
                }
            }
        }

        ConversationSettingsDialog {
            id: settingsDialog
        }
    }
}