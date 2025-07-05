import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: historyList
    width: parent ? parent.width : 400
    color: "#fff"
    radius: 8
    border.color: "#e0e0e0"
    border.width: 1
    clip: true

    // Properties
    property bool sidebarVisible: false
    property bool initializedSidebar: false

    property var conversation_data: []

    signal conversationOpened()


//---------------------- History List ----------------------//
    RowLayout {
        anchors.fill: parent
        anchors.margins: 0
        spacing: 0
        
        // Điều chỉnh tỷ lệ cho các thành phần
        Layout.fillWidth: true
        Layout.fillHeight: true
        ListView {
            id: history_view
            Layout.preferredWidth: parent ? parent.width * 0.3 : 300
            Layout.minimumWidth: 250
            Layout.fillHeight: true
            Layout.margins: 10
            model: historyModel
            clip: true
            spacing: 12
            boundsBehavior: Flickable.StopAtBounds
            
            // Property to track if user is viewing the top of the list
            property bool atBeginning: true // Default to true for initial load
            
            // Monitor scroll position
            onContentYChanged: {
                atBeginning = contentY < 50
            }

            delegate: Rectangle {
                width: history_view.width
                height: contentColumn.height + 32
                color: ListView.isCurrentItem ? "#e3f2fd" : (index % 2 === 0 ? "#f9f9f9" : "#ffffff")
                border.color: ListView.isCurrentItem ? "#2196f3" : "#e0e0e0"
                border.width: 1
                radius: 5
                anchors.leftMargin: 4
                anchors.rightMargin: 4
                anchors.topMargin: 6
                anchors.bottomMargin: 6
                
                Column {
                    id: contentColumn
                    width: parent.width - 20
                    anchors.centerIn: parent
                    spacing: 10
                    
                    RowLayout {
                        width: parent.width
                        spacing: 10
                        
                        // Date and time
                        Text {
                            text: model.date
                            font.pixelSize: 13
                            font.bold: true
                            Layout.preferredWidth: 150
                        }
                        
                        Item { Layout.fillWidth: true }
                    }
                    
                    // Conversation preview
                    Rectangle {
                        width: parent.width
                        height: previewText.height + 16
                        color: "#f5f5f5"
                        radius: 4
                        
                        Text {
                            id: previewText
                            width: parent.width - 16
                            anchors.centerIn: parent
                            text: model.preview
                            font.pixelSize: 12
                            wrapMode: Text.WordWrap
                            elide: Text.ElideRight
                            maximumLineCount: 2
                        }
                    }
                }
                MouseArea {
                    anchors.fill: parent
                    onClicked: {
                        // Only change conversation if not already selected
                        if (history_view.currentIndex !== index) {
                            history_view.currentIndex = index
                            historyModel.changeConversation(model.id)
                        }
                    }
                    cursorShape: Qt.PointingHandCursor
                }
            }

            ScrollBar.vertical: ScrollBar {
                policy: ScrollBar.AsNeeded
            }
            
            // Empty state
            Text {
                anchors.centerIn: parent
                text: "No conversation history"
                font.pixelSize: 16
                color: "#999"
                visible: history_view.count === 0
            }
        }

        Rectangle {
            Layout.margins: 10
            width: 1
            color: "#e0e0e0"
            Layout.fillHeight: true
        }

        ConversationView {
            id: conversation_view
            Layout.preferredWidth: parent ? parent.width * 0.7 : 500
            Layout.minimumWidth: 350
            Layout.fillHeight: true
            Layout.fillWidth: true
            Layout.rightMargin: 10
            Layout.leftMargin: 0
            Layout.topMargin: 10
            Layout.bottomMargin: 10
            conversationData: historyList.conversation_data
            otherSpeakerColor: "#888"
            userSpeakerColor: "#2e7d32"
        }
    }

    // Conversation Connections
    Connections {
        target: historyModel
        function onConversationDataChanged() {
            // Kiểm tra trạng thái cuộc hội thoại hiện tại
            var wasAtEnd = conversation_view.atEnd
            
            // Cập nhật dữ liệu
            historyList.conversation_data = historyModel.getConversationData()
            
            // Đợi cập nhật hoàn tất và cập nhật vị trí cuộn nếu cần
            refreshTimer.wasAtEnd = wasAtEnd
            refreshTimer.restart()
            
            // Báo hiệu rằng một cuộc hội thoại đã được mở
            historyList.conversationOpened()
        }
        
        // Xử lý khi historyModel thay đổi (thêm/xóa cuộc hội thoại)
        function onLayoutChanged() {
            // Lưu trữ vị trí cuộn hiện tại
            var scrollPos = history_view.contentY
            
            // Chỉ cập nhật vị trí xem nếu người dùng đang ở đầu danh sách
            if (history_view.atBeginning) {
                // Sử dụng Qt.callLater để đảm bảo dữ liệu đã được cập nhật trước khi cuộn
                Qt.callLater(function() {
                    history_view.positionViewAtBeginning()
                })
            } else {
                // Sử dụng timer để khôi phục vị trí cuộn
                historyScrollTimer.scrollPos = scrollPos
                historyScrollTimer.restart()
            }
        }
    }
    
    // Timer để xử lý cập nhật giao diện cho cuộc hội thoại
    Timer {
        id: refreshTimer
        interval: 50
        property bool wasAtEnd: false
        
        onTriggered: {
            // Nếu người dùng đang ở cuối danh sách, cuộn xuống cuối
            if (wasAtEnd) {
                Qt.callLater(function() {
                    conversation_view.scrollToEnd()
                })
            }
            // Không cần khôi phục vị trí cuộn vì ConversationView đã xử lý điều này
        }
    }
    
    // Timer để xử lý cập nhật vị trí cuộn cho history view
    Timer {
        id: historyScrollTimer
        interval: 50
        property real scrollPos: 0
        
        onTriggered: {
            Qt.callLater(function() {
                history_view.contentY = scrollPos
            })
        }
    }

//---------------------- History Action ----------------------//
    ConversationActionBar {
        id: actionBar
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        
        showSummaryButton: true
        showClearButton: false
        showRenameButton: true
        showNewButton: false
        
        onSummaryClicked: showSummary()
        onRenameClicked: sidebarVisible = !sidebarVisible
    }

//---------------------- Rename Speacker Sidebar ----------------------//
    RenameSpeakerSideBar {
        id: speakerSidebar
        visible: true
        speakerModel: []
        onSpeakerRenamed: function(speakerId, newName) {
            historyModel.updateSpeakerName(speakerId, newName)
        }
        onHideSidebar: {
            sidebarVisible = false
        }
    }

    onSidebarVisibleChanged: {
        if (initializedSidebar) {
            speakerSidebar.isVisible = sidebarVisible
            if (sidebarVisible) {
                speakerSidebar.speakerModel = historyModel.getUniqueSpeakerMaps()
            }
        }
    }

    // Rename Speaker Connections
    Connections {
        target: historyModel
        function onUniqueSpeakersChanged() {
            if (sidebarVisible) {
                speakerSidebar.speakerModel = historyModel.getUniqueSpeakerMaps()
            }
        }
    }


//---------------------- Summary PopUp ----------------------//
    PopUpSummary {
        id: summaryPopup
        title: "Summary Conversation"
        okText: "Close"
        showCancelButton: false

        Component.onCompleted: {
        }
    }

    function showSummary() {
        summaryPopup.setLoading(true)
        summaryPopup.open()
        historyModel.summarizeConversation()
    }

    // Summary PopUp Connections
    Connections {
        target: historyModel
        function onSummaryReady(text) {
            summaryPopup.setLoading(false)
            summaryPopup.setResult(text)
        }
        function onSummaryError(err) {
            summaryPopup.setLoading(false)
            summaryPopup.setContent("Error: " + err)
        }
    }

    // Initialize sidebar and load conversation data
    Component.onCompleted: {
        initializedSidebar = true
        if (historyModel && historyModel.getConversationData) {
            conversation_data = historyModel.getConversationData()
        }

        if (historyModel && historyModel.getUniqueSpeakerMaps) {
            speakerSidebar.speakerModel = historyModel.getUniqueSpeakerMaps()
        }
    }
}
