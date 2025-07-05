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
        
        if not self._checkSpeakerExisted(speaker_Id=speaker):
            self._addNewSpeaker(speaker_Id=speaker, speaker_Name="UNKNOWN USER")

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
            self._save_speaker_map_to_file()

    def _checkSpeakerExisted(self, speaker_Id: str) -> bool:
        return any(s.get("speaker_Id") == speaker_Id for s in self._unique_speaker_map)

    def _save_conversation_to_file(self):
        try:
            HISTORY_PATH.mkdir(parents=True, exist_ok=True)
            save_file = HISTORY_PATH / self._history_save_file
            with open(save_file, 'w', encoding='utf-8') as f:
                json.dump(self._data, f, ensure_ascii=False, indent=4)
            self.conversationSaved.emit()
        except IOError as e:
            pass

    def _save_speaker_map_to_file(self):
        try:
            SPEAKER_PATH.mkdir(parents=True, exist_ok=True)
            save_file = SPEAKER_PATH / self._history_save_file
            with open(save_file, 'w', encoding='utf-8') as f:
                json.dump(self._unique_speaker_map, f, ensure_ascii=False, indent=4)
            self.conversationSaved.emit()
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
        self._data.clear()
        self._unique_speaker_map.clear()
        self._history_save_file = f"{str(uuid.uuid4())}.json"


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

            system_content = """
                You are an intelligent assistant specialized in analyzing and summarizing conversations between multiple speakers.

                Your task is to:
                - Carefully read the provided conversation data (in JSON format)
                - Understand the context and flow of discussion
                - Identify the key points, decisions, actions, questions, or ideas mentioned
                - Eliminate filler phrases or repetitive small talk
                - Present a concise, clear summary that captures the essential meaning of the conversation

                The conversation is structured in JSON format. Each item represents a single utterance and includes:
                - speaker: the participant's identifier (e.g., SPEAKER_1)
                - origin_text: the original spoken sentence
                - translated_text: the translated version (if applicable)
                - direction: indicates whether the sentence is from the user or others
                - timestamp: when the sentence occurred

                Guidelines:
                - Use the **original text** (`origin_text`) as the primary content to analyze
                - Refer to `speaker` names when relevant (especially when clarifying who said what)
                - Format the output as a **short paragraph** or a **bulleted list**, depending on what's more natural
                - Make the summary sound like a brief meeting note or professional recap
                - Do **not** repeat every line; instead, group related points and summarize them meaningfully
                - If no meaningful content is found, respond with: "No significant information to summarize."

                Example output formats:
                - Paragraph: "The participants discussed X, Y, and Z. They agreed on A and raised concerns about B."
                - Bulleted list:
                - Point A: ...
                - Point B: ...

                Be accurate, neutral, and clear in your language.
            """

            speaker_map = {s["speaker_Id"]: s["speaker_Name"] for s in self._unique_speaker_map}
            data_with_names = [
                {**item, "speaker": speaker_map.get(item.get("speaker", ""), item.get("speaker", ""))}
                for item in self._data
            ]
            conv_content = json.dumps(data_with_names, ensure_ascii=False, indent=2)
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
