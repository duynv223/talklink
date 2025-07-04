from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt, Slot, Signal
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

    uniqueSpeakersChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._history_data = []
        self._conversation_data = []
        self._unique_speaker_map = []
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
        self._unique_speaker_map.clear()
        
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
                conv_id = conv_file.name
                
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
                            self._unique_speaker_map = speaker_data

                self._history_data.append({
                    "id": conv_id,
                    "date": date_str,
                    "preview": preview
                })
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error processing file {conv_file}: {e}")

        self.endResetModel()

    def changeConversation(self, id):
        self.beginResetModel()
        self._history_data.clear()
        self._conversation_data.clear()
        self._unique_speaker_map.clear()
        
        if not HISTORY_PATH.exists():
            self.endResetModel()
            return

        conv_file = HISTORY_PATH / id
        with open(conv_file, 'r', encoding='utf-8') as f:
            conv_data = json.load(f)
            self._conversation_data = conv_data

        speaker_file = SPEAKER_PATH / id
        if speaker_file.exists():
            with open(speaker_file, 'r', encoding='utf-8') as f:
                speaker_data = json.load(f)
                self._unique_speaker_map = speaker_data
        self.endResetModel()

    def _getSpeakerName(self, speaker_Id: str):
        return next(
            (speaker["speaker_Name"] for speaker in self._unique_speaker_map if speaker.get("speaker_Id") == speaker_Id), "UNKNOWN USER"
        )

    def _addNewSpeaker(self, speaker_Id: str, speaker_Name: str = "UNKOWN USER"):
        if not self._checkSpeakerExisted(speaker_Id):
            self._unique_speaker_map.append({
                "speaker_Id": speaker_Id,
                "speaker_Name": speaker_Name
            })
            self.uniqueSpeakersChanged.emit()

    def _checkSpeakerExisted(self, speaker_Id: str) -> bool:
        return any(s.get("speaker_Id") == speaker_Id for s in self._unique_speaker_map)

    def _save_conversation_to_file(self):
        try:
            HISTORY_PATH.mkdir(parents=True, exist_ok=True)
            save_file = HISTORY_PATH / self._history_save_file
            with open(save_file, 'w', encoding='utf-8') as f:
                json.dump(self._data, f, ensure_ascii=False, indent=4)
        except IOError as e:
            pass

    def _save_speaker_map_to_file(self):
        try:
            SPEAKER_PATH.mkdir(parents=True, exist_ok=True)
            save_file = SPEAKER_PATH / self._history_save_file
            with open(save_file, 'w', encoding='utf-8') as f:
                json.dump(self._unique_speaker_map, f, ensure_ascii=False, indent=4)
        except IOError as e:
            pass

    @Slot(result='QVariantList')
    def getUniqueSpeakerMaps(self):
        return self._unique_speaker_map

    @Slot(str, str)
    def updateSpeakerName(self, speaker_Id, speaker_Name):
        updated = False
        for speaker in self._unique_speaker_map:
            if speaker.get("speaker_Id") == speaker_Id:
                speaker["speaker_Name"] = speaker_Name
                updated = True
                break
        if updated:
            self.uniqueSpeakersChanged.emit()
            if self.rowCount() > 0:
                top = self.index(0, 0)
                bottom = self.index(self.rowCount() - 1, 0)
                self.dataChanged.emit(top, bottom, [self.SpeakerRole])
            self._save_speaker_map_to_file()