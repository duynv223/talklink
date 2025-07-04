from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt, QStandardPaths, Slot, Signal
import json
from pathlib import Path
import uuid
import time
import asyncio

BASE_PATH = Path(__file__).resolve().parent.parent.parent
HISTORY_PATH = BASE_PATH / "conversations"
SUMMARY_PATH = BASE_PATH / "summaries"
SPEAKER_PATH = BASE_PATH / "speaker"

class ConversationModel(QAbstractListModel):
    IdRole = Qt.UserRole + 1
    TimeStampRole = Qt.UserRole + 2
    SpeakerRole = Qt.UserRole + 3
    DirectionRole = Qt.UserRole + 4
    OriginTextRole = Qt.UserRole + 5
    TranslatedTextRole = Qt.UserRole + 6

    uniqueSpeakersChanged = Signal()
    conversationSaved = Signal()

    summaryReady = Signal(str)
    summaryError = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._data = [
            {
                "id": str(uuid.uuid4()), 
                "timestamp": time.time(), 
                "speaker": "SPEAKER_3",
                "direction": "You", 
                "origin_text": "Hello!", 
                "translated_text": "Xin chào!"
            }
        ]

        self._unique_speaker_map = [
            {"speaker_Id": "SPEAKER_1", "speaker_Name": "System"},
            {"speaker_Id": "SPEAKER_2", "speaker_Name": "Other"},
            {"speaker_Id": "SPEAKER_3", "speaker_Name": "SomeOne"},
        ]

        self._history_save_file = f"{str(uuid.uuid4())}.json"

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
            speaker_id = item.get("speaker", "")
            speaker_name = self._getSpeakerName(speaker_Id=speaker_id)
            if speaker_name == "UNKOWN USER":
                return speaker_id
            else:
                return speaker_name
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
                "timestamp": timestamp,
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
        if id is None:
            return False

        for i, sentence in enumerate(self._data):
            if sentence.get("id") == id:
                self._data[i] = {
                    "id": id,
                    "timestamp": timestamp if timestamp else sentence.get("timestamp"),
                    "speaker": speaker if speaker is not None else sentence.get("speaker"),
                    "origin_text": origin_text if origin_text is not None else sentence.get("origin_text"),
                    "translated_text": translated_text if translated_text is not None else sentence.get("translated_text"),
                    "direction": direction if direction is not None else sentence.get("direction"),
                }

                index = self.index(i, 0)
                roles = [
                    self.IdRole,
                    self.TimeStampRole,
                    self.SpeakerRole,
                    self.DirectionRole,
                    self.OriginTextRole,
                    self.TranslatedTextRole,
                ]
                self.dataChanged.emit(index, index, roles)
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
        if speaker is None:
            speaker = "UNKNOWN_USER"
            self._addNewSpeaker(speaker)

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
        self._save_conversation_to_file()

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

    @Slot()
    def new_conversation(self):
        self._save_conversation_to_file()
        self._save_speaker_map_to_file()
        self._history_save_file = f"{str(uuid.uuid4())}.json"
        self.clear()
        self.conversationSaved.emit()


    @Slot()
    def clear(self):
        self.beginRemoveRows(QModelIndex(), 0, self.rowCount() - 1)
        self._data.clear()
        self.endRemoveRows()
        self._save_conversation_to_file()

    @Slot()
    def summarizeConversation(self):
        asyncio.create_task(self._do_summary())

    async def _do_summary(self):
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(base_url="https://aiportalapi.stu-platform.live/jpe", api_key="sk-B8guBxC5737sXsR3sJGKmw")

            system_content = f"""
                You are an AI assistant specialized in summarizing conversations involving multiple speakers.
                Generate a short and concise summary that captures the key points discussed.
                Include speaker names if they are important for understanding the context.
                Avoid repeating every sentence — focus only on the essential ideas, presented in a clear and easy-to-read format, like a condensed meeting note.
                The conversation content is presented in JSON format, where each object represents a sentence, including both the original text and the translated text.
            """

            conv_content = json.dumps(self._data, ensure_ascii=False, indent=2)
            messages = [
                {"role": "system", "content": system_content},
                {"role": "user", "content": conv_content}
            ]

            res = await client.chat.completions.create(
                model="GPT-4o-mini",
                messages=messages
            )
            summary = res.choices[0].message.content.strip()
            self.summaryReady.emit(summary)

        except Exception as e:
            self.summaryError.emit(str(e))
