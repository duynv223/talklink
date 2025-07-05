import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Popup {
    id: commonPopup
    
    // Position and size
    width: dialogWidth
    height: dialogHeight
    anchors.centerIn: parent
    modal: true
    focus: true
    closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside
    padding: 20
    
    // Public properties for customization
    property int dialogWidth: parent ? parent.width * 0.75 : 700
    property int dialogHeight: parent ? parent.height * 0.6 : 500
    property string title: "Dialog"
    property string content: ""
    property string result: ""
    property bool loading: false
    property color backgroundColor: "#ffffff"
    property color borderColor: "#cccccc"
    property int borderRadius: 10
    property bool showOkButton: true
    property bool showCancelButton: false
    property string okText: "OK"
    property string cancelText: "Cancel"
    
    // Signals
    signal accepted()
    signal rejected()
    signal popupOpened()
    signal popupClosed()
    
    // Background
    background: Rectangle {
        color: backgroundColor
        radius: borderRadius
        border.color: borderColor
        border.width: 1
    }
    
    // Slots/Functions
    function setLoading(isLoading) {
        loading = isLoading
    }
    
    function setContent(newContent) {
        content = newContent
    }
    
    function setResult(newResult) {
        result = newResult
    }
    
    // Connect to built-in signals
    onOpened: popupOpened()
    onClosed: popupClosed()

    ColumnLayout {
        anchors.fill: parent
        spacing: 12

        // Title
        Label {
            text: title
            font.pixelSize: 18
            font.bold: true
            Layout.alignment: Qt.AlignHCenter
            horizontalAlignment: Text.AlignHCenter 
        }

        // Loading indicator
        Loader {
            active: loading
            sourceComponent: busyIndicatorComponent
            Layout.alignment: Qt.AlignHCenter
            visible: loading
        }

        // Content text (if provided)
        TextEdit {
            visible: !loading && content.length > 0
            text: content
            wrapMode: TextEdit.Wrap
            font.pixelSize: 14
            color: "#333"
            readOnly: true
            selectByMouse: true
            Layout.fillWidth: true
        }

        // Result text (from API)
        ScrollView {
            visible: !loading && result.length > 0
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            
            TextEdit {
                width: commonPopup.width - 40
                text: result
                wrapMode: TextEdit.Wrap
                font.pixelSize: 14
                color: "#333"
                readOnly: true
                selectByMouse: true
            }
        }

        // Button bar
        RowLayout {
            Layout.alignment: Qt.AlignRight
            Layout.fillWidth: true
            
            Button {
                visible: showCancelButton
                text: cancelText
                onClicked: {
                    rejected()
                    commonPopup.close()
                }
            }
            
            Button {
                visible: showOkButton
                text: okText
                highlighted: true
                onClicked: {
                    accepted()
                    commonPopup.close()
                }
            }
        }
    }

    // BusyIndicator component
    Component {
        id: busyIndicatorComponent
        Item {
            width: 40
            height: 40
            BusyIndicator {
                running: true
                anchors.centerIn: parent
            }
        }
    }
}