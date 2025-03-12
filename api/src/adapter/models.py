import uuid
from typing import Optional
from datetime import datetime as dt, timezone

from pydantic import BaseModel, Field
from enum import Enum
from common_utils.schemas import Message


class WsOutMessageType(Enum):
    RESPONSE = "response"
    EVENT = "event"


class WsOutMessage(BaseModel):
    type: WsOutMessageType


class WsOutResponse(WsOutMessage):
    type: WsOutMessageType = WsOutMessageType.RESPONSE
    id: str
    data: dict


class WsEventType(Enum):
    STATUS_MESSAGE = "statusMessage"
    NEW_MESSAGE = "newMessage"



class WsOutEvent(WsOutMessage):
    type: WsOutMessageType = WsOutMessageType.EVENT
    event: WsEventType
    data: dict

    @classmethod
    def from_message(cls, message: Message) -> "WsOutEvent":
        if message.is_response_message():
            return WsNewMessageEvent(
                data=MessageData(
                    user_message_id=message.user_message_id,
                    text=message.response,
                    countries=message.countries

                )
            )
        if message.is_status_message():
            return WsStatusEvent(
                data=StatusMessageData(
                    user_message_id=message.user_message_id,
                    text=message.text,
                )
            )


class StatusMessageData(BaseModel):
    user_message_id: str
    text: str


class WsStatusEvent(WsOutEvent):
    event: WsEventType = WsEventType.STATUS_MESSAGE
    data: StatusMessageData



class MessageData(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    datetime: dt = Field(default_factory=lambda: dt.now(tz=timezone.utc))
    user_message_id: str
    text: str
    countries: Optional[list] = None


class WsNewMessageEvent(WsOutEvent):
    event: WsEventType = WsEventType.NEW_MESSAGE
    data: MessageData
