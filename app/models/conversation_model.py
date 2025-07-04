from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt

import uuid
import time

class ConversationModel(QAbstractListModel):
    IdRole = Qt.UserRole + 1
    TimeStampRole = Qt.UserRole + 2
    SpeakerRole = Qt.UserRole + 3
    DirectionRole = Qt.UserRole + 4
    OriginTextRole = Qt.UserRole + 5
    TranslatedTextRole = Qt.UserRole + 6

    def __init__(self, parent=None):
        super().__init__(parent)
        self._data = [
            {
                "id": str(uuid.uuid4()), 
                "timestamp": time.time(), 
                "speaker": "System", 
                "direction": "System", 
                "origin_text": "Hello!", 
                "translated_text": "Xin chào!"
            }
        ]

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def data(self, index, role):
        if not index.isValid():
            return None
        item = self._data[index.row()]
        if role == self.IdRole:
            return item.get("id", "")
        elif role == self.TimeStampRole:
            timestamp = item.get("timestamp", time.time())
            if isinstance(timestamp, (int, float)):
                return time.strftime("%H:%M:%S", time.localtime(timestamp))
            return str(timestamp)
        elif role == self.SpeakerRole:
            return item.get("speaker", "")
        elif role == self.DirectionRole:
            return item.get("direction", "")
        elif role == self.OriginTextRole:
            return item.get("origin_text", "")
        elif role == self.TranslatedTextRole:
            return item.get("translated_text", "") 
      
        return None

    def roleNames(self):
        return {
            self.IdRole: b"id",
            self.TimeStampRole: b"timestamp",
            self.SpeakerRole: b"speaker",
            self.DirectionRole: b"direction",
            self.OriginTextRole: b"originText",
            self.TranslatedTextRole: b"translatedText",
        }

    def append(self,
        id: str = None, 
        timestamp: float = None, 
        speaker: str = None, 
        origin_text: str = None, 
        translated_text: str = None, 
        direction: str = None
    ):
        self.beginInsertRows(QModelIndex(), len(self._data), len(self._data))
        self._data.append(
            {
                "id": id,
                "timestamp": time.strftime("%H:%M:%S", time.localtime(timestamp)),
                "speaker": speaker,
                "origin_text": origin_text,
                "translated_text": translated_text,
                "direction": direction
            }
        )
        self.endInsertRows()

    def update(self,
        id: str = None, 
        timestamp: float = None, 
        speaker: str = None, 
        origin_text: str = None, 
        translated_text: str = None, 
        direction: str = None
    ):
        print(f"KhoiTV$--------self._data: {self._data}")
        print(f"KhoiTV$--------id: {id}")
        print(f"KhoiTV$--------timestamp: {timestamp}")
        print(f"KhoiTV$--------speaker: {speaker}")
        print(f"KhoiTV$--------origin_text: {origin_text}")
        print(f"KhoiTV$--------translated_text: {translated_text}")
        print(f"KhoiTV$--------direction: {direction}")
        if id is not None:
            sentence_id_to_find = id
            for i, existing_sentence in enumerate(self._data):
                if existing_sentence["id"] == sentence_id_to_find:

                    self._data[i] = {
                        "id": id,
                        "timestamp": time.strftime("%H:%M:%S", time.localtime(timestamp)),
                        "speaker": speaker,
                        "origin_text": origin_text,
                        "translated_text": translated_text,
                        "direction": direction
                    }
                    model_index = self.index(i, 0)
                    self.dataChanged.emit(model_index, model_index, [self.IdRole, self.TimeStampRole, self.SpeakerRole, self.DirectionRole, self.OriginTextRole, self.TranslatedTextRole])
                    return True
        return False

    def upsert(self,
        id: str = None, 
        timestamp: float = None, 
        speaker: str = None, 
        origin_text: str = None, 
        translated_text: str = None, 
        direction: str = None
    ):
        was_updated = self.update(
            id=id, 
            timestamp=timestamp, 
            speaker=speaker, 
            origin_text=origin_text, 
            translated_text=translated_text, 
            direction=direction
        )
        if not was_updated:
            self.append(
                id=id, 
                timestamp=timestamp, 
                speaker=speaker, 
                origin_text=origin_text, 
                translated_text=translated_text, 
                direction=direction
            )
