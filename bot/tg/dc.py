
from pydantic import BaseModel


class Chat(BaseModel):
    id: int # noqa: A003


class Message(BaseModel):
    chat: Chat
    text: str


class UpdateObj(BaseModel):
    update_id: int
    message: Message


class GetUpdatesResponse(BaseModel):
    ok: bool
    result: list[UpdateObj]  # todo


class SendMessageResponse(BaseModel):
    ok: bool
    result: Message  # todo
