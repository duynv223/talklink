import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

RowLayout {
	id: statusBar
	Layout.alignment: Qt.AlignRight | Qt.AlignBottom
	Layout.fillWidth: true
	spacing: 16

	Rectangle {
		color: "#f0f0f0"
		radius: 6
		border.color: "#cccccc"
		border.width: 1
		height: 28
		Layout.fillWidth: true

		RowLayout {
			anchors.fill: parent
			anchors.margins: 6
			spacing: 12

			Text { text: "State: "; color: "#666" }
			Text { id: stateText; text: pipeline.appState || "Idle"; color: "#222" }

			Item { Layout.fillWidth: true }

			RowLayout {
				visible: pipeline.actionState && pipeline.actionState !== "Idle"
				spacing: 2
				Text { text: "Action: "; color: "#666" }
				Text { id: actionText; text: pipeline.actionState; color: "#222" }
			}
			RowLayout {
				visible: pipeline.errorMessage && pipeline.errorMessage !== ""
				spacing: 2
				Text { text: "Error: "; color: "#666" }
				Text { id: errorText; text: pipeline.errorMessage; color: "#c00" }
			}
		}
	}
}
