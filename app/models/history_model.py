from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt, Slot, Signal
import json
from pathlib import Path
import time
import asyncio
import json

BASE_PATH = Path(__file__).resolve().parent.parent.parent
HISTORY_PATH = BASE_PATH / "conversations"
SPEAKER_PATH = BASE_PATH / "speaker"

class HistoryModel(QAbstractListModel):
    IdRole = Qt.UserRole + 1
    DateRole = Qt.UserRole + 2
    PreviewRole = Qt.UserRole + 3

    uniqueSpeakersChanged = Signal()
    conversationDataChanged = Signal()

    summaryReady = Signal(str)
    summaryError = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._history_data = []
        self._conversation_data = []
        self._unique_speaker_map = []
        self.refresh()

    def rowCount(self, parent=QModelIndex()):
        return len(self._history_data)

    def data(self, index, role):
        if not index.isValid() or not (0 <= index.row() < len(self._history_data)):
            return None
        item = self._history_data[index.row()]
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

    @Slot(str)
    def changeConversation(self, id):
        self._conversation_data.clear()
        self._unique_speaker_map.clear()
        
        if not HISTORY_PATH.exists():
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

        self.conversationDataChanged.emit()
        self.uniqueSpeakersChanged.emit()


    def _getSpeakerName(self, speaker_Id: str):
        return next(
            (speaker["speaker_Name"] for speaker in self._unique_speaker_map if speaker.get("speaker_Id") == speaker_Id), "UNKNOWN USER"
        )

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
    def getConversationData(self):
        speaker_map = {
            s["speaker_Id"]: s["speaker_Name"]
            for s in self._unique_speaker_map
        }

        data_with_names = []
        for item in self._conversation_data:
            new_item = item.copy()
            speaker_id = new_item.get("speaker", "")
            new_item["speaker"] = speaker_map.get(speaker_id, speaker_id)
            timestamp = new_item.get("timestamp", 0)
            new_item["timestamp"] = time.strftime("%H:%M:%S", time.localtime(timestamp))
            data_with_names.append(new_item)

        return data_with_names


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
            self.conversationDataChanged.emit()
            self.uniqueSpeakersChanged.emit()
            self._save_speaker_map_to_file()


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
                for item in self._conversation_data
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