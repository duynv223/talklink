from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt

class ConversationModel(QAbstractListModel):
    SpeakerRole = Qt.UserRole + 1
    TextRole = Qt.UserRole + 2

    def __init__(self, parent=None):
        super().__init__(parent)
        self._data = [{"speaker": "System", "text": "Hello!"}]

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def data(self, index, role):
        if not index.isValid():
            return None
        row = index.row()
        item = self._data[row]
        if role == self.SpeakerRole:
            return item["speaker"]
        if role == self.TextRole:
            return item["text"]
        return None

    def roleNames(self):
        return {
            self.SpeakerRole: b"speaker",
            self.TextRole: b"text"
        }

    def append(self, speaker, text):
        self.beginInsertRows(QModelIndex(), len(self._data), len(self._data))
        self._data.append({"speaker": speaker, "text": text})
        self.endInsertRows()

    def update(self, index, speaker, text):
        if 0 <= index < len(self._data):
            self._data[index] = {"speaker": speaker, "text": text}
            top_left = self.index(index, 0)
            bottom_right = self.index(index, 0)
            self.dataChanged.emit(top_left, bottom_right, self.roleNames().keys())
