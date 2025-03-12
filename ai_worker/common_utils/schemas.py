import json
import uuid
from enum import Enum
from pydantic import BaseModel, Field
from typing import TypeGuard, Optional
from aio_pika import Message as RabbitMessage


class MessageType(Enum):
    USER_MESSAGE = "user_message"
    STATUS_MESSAGE = "status_message"
    RESPONSE_MESSAGE = "response_message"


class WsAuthRequest(BaseModel):
    chat_id: str | None = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str

class WsAuthResponse(BaseModel):
    ws_url: str


class Message(BaseModel):
    chat_id: str
    type: MessageType

    def prepare(self):
        return RabbitMessage(self.model_dump_json().encode("utf-8"))

    @classmethod
    def from_rabbit_message(cls, message: RabbitMessage) -> "Message":
        message_str = message.body.decode("utf-8")
        message_dict = json.loads(message_str)
        message_type = Message(**message_dict).type

        return MESSAGE_TYPE_TO_CLASS[message_type](**message_dict)

    def is_user_message(self) -> TypeGuard["UserMessage"]:
        return self.type == MessageType.USER_MESSAGE

    def is_status_message(self) -> TypeGuard["StatusMessage"]:
        return self.type == MessageType.STATUS_MESSAGE

    def is_response_message(self) -> TypeGuard["ResponseMessage"]:
        return self.type == MessageType.RESPONSE_MESSAGE


class UserMessage(Message):
    type: MessageType = MessageType.USER_MESSAGE
    message_id: str
    artist: str
    title: str


class StatusMessage(Message):
    type: MessageType = MessageType.STATUS_MESSAGE
    user_message_id: str
    text: str


class ResponseMessage(Message):
    type: MessageType = MessageType.RESPONSE_MESSAGE
    user_message_id: str
    response: str
    countries: list





MESSAGE_TYPE_TO_CLASS = {
    MessageType.USER_MESSAGE: UserMessage,
    MessageType.STATUS_MESSAGE: StatusMessage,
    MessageType.RESPONSE_MESSAGE: ResponseMessage
}