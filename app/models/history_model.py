from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt, Slot
import json
from pathlib import Path
import time

BASE_PATH = Path(__file__).resolve().parent.parent.parent
HISTORY_PATH = BASE_PATH / "conversations"
SPEAKER_PATH = BASE_PATH / "speaker"

class HistoryModel(QAbstractListModel):
    IdRole = Qt.UserRole + 1
    DateRole = Qt.UserRole + 2
    PreviewRole = Qt.UserRole + 3

    def __init__(self, parent=None):
        super().__init__(parent)
        self._history_data = []
        self._conversation_data = []
        self._speaker_map_data = []
        # self.refresh()

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def data(self, index, role):
        if not index.isValid() or not (0 <= index.row() < len(self._data)):
            return None
        item = self._data[index.row()]
        if role == self.IdRole:
            return item.get("id", "")
        elif role == self.DateRole:
            return item.get("date", "")
        elif role == self.PreviewRole:
            return item.get("preview", "")
        return None

    def roleNames(self):
        return {
            self.IdRole: b"id",
            self.DateRole: b"date",
            self.PreviewRole: b"preview",
        }

    @Slot()
    def refresh(self):
        self.beginResetModel()
        self._history_data.clear()
        self._conversation_data.clear()
        self._speaker_map_data.clear()
        
        if not HISTORY_PATH.exists():
            self.endResetModel()
            return

        conversation_files = sorted(
            [f for f in HISTORY_PATH.glob("*.json")],
            key=lambda f: f.stat().st_mtime,
            reverse=True
        )

        for i, conv_file in enumerate(conversation_files):
            try:
                conv_id = conv_file.stem
                
                # Date from file modification time
                mtime = conv_file.stat().st_mtime
                date_str = time.strftime("%B %d, %Y - %I:%M %p", time.localtime(mtime))

                # Preview from conversation data
                with open(conv_file, 'r', encoding='utf-8') as f:
                    conv_data = json.load(f)
                    if i == 0:
                        self._conversation_data = conv_data
                preview = " ".join(item.get("origin_text", "") for item in conv_data[:2]).strip()

                speaker_file = SPEAKER_PATH / f"{conv_id}.json"
                if speaker_file.exists():
                    with open(speaker_file, 'r', encoding='utf-8') as f:
                        speaker_data = json.load(f)
                        if i == 0:
                            self._speaker_map_data = speaker_data

                self._history_data.append({
                    "id": conv_id,
                    "date": date_str,
                    "preview": preview,
                    "conversation_file_name": conv_file.name,
                })
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error processing file {conv_file}: {e}")

        self.endResetModel()

