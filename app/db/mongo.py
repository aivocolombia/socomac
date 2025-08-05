from langchain.schema import BaseChatMessageHistory, AIMessage, HumanMessage, BaseMessage
from pymongo import MongoClient
from typing import List
from dotenv import load_dotenv
import os

load_dotenv()



class MongoChatMessageHistory(BaseChatMessageHistory):
    def __init__(self, phone: str, db_uri=os.getenv("MONGO_URI"), db_name="chat_memory2"):
        print("Inicializando MongoChatMessageHistory")

        self.phone = phone
        print(self.phone)
        self.client = MongoClient(db_uri)
        self.collection = self.client[db_name]["conversations"]
    @property
    def messages(self) -> List[BaseMessage]:
        doc = self.collection.find_one({"phone": self.phone, "status": "open"})
        if not doc:
            return []
        return [self._deserialize_message(m) for m in doc.get("messages", [])]

    def add_message(self, message: BaseMessage) -> None:
        msg_obj = self._serialize_message(message)
        self.collection.update_one(
            {"phone": self.phone, "status": "open"},
            {"$push": {"messages": msg_obj}},
            upsert=True
        )

    def clear(self) -> None:
        self.collection.update_one(
            {"phone": self.phone, "status": "open"},
            {"$set": {"messages": []}},
        )

    def _serialize_message(self, message: BaseMessage) -> dict:
        return {
            "type": message.type,
            "data": {"content": message.content}
        }

    def _deserialize_message(self, raw: dict) -> BaseMessage:
        if raw["type"] == "human":
            return HumanMessage(content=raw["data"]["content"])
        elif raw["type"] == "ai":
            return AIMessage(content=raw["data"]["content"])
        else:
            raise ValueError(f"Tipo de mensaje desconocido: {raw['type']}")
