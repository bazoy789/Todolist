from typing import Callable, Any

from django.core.management.base import BaseCommand
from pydantic import BaseModel

from bot.models import TgUser
from bot.tg.client import TgClient
from bot.tg.dc import Message
from goals.models import Goal, GoalCategory


class FSMData(BaseModel):
    next_handler: Callable
    data: dict[str, Any] = {}


class Command(BaseCommand):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.tg_client: TgClient = TgClient()
        self.data_client: dict[int, FSMData] = {}

    def handle(self, *args: Any, **options: Any) -> None:
        offset: int = 0

        while True:
            res = self.tg_client.get_updates(offset=offset)
            for item in res.result:
                offset = item.update_id + 1
                self.handler_message(item.message)

    def handler_message(self, msg: Message) -> None:
        tg_user, created = TgUser.objects.get_or_create(chat_id=msg.chat.id)
        if tg_user.user:
            self.handler_authorized_user(tg_user, msg)
        else:
            self.handler_unauthorized_user(tg_user, msg)

    def handler_unauthorized_user(self, tg_user: TgUser, msg: Message) -> None:
        ver_code: str = TgUser.gen_verification_code()
        tg_user.verification_code = ver_code
        tg_user.save()

        self.tg_client.send_message(
            chat_id=msg.chat.id,
            text=f"Код верификации -> {ver_code}"
        )

    def handler_authorized_user(self, tg_user: TgUser, msg: Message) -> None:
        if msg.text.startswith("/"):
            if msg.text == "/goals":
                self.goal_all(tg_user, msg)
            elif msg.text == "/create":
                self.goal_category_all(tg_user, msg)
            elif msg.text == "/cancel":
                self.data_client.pop(tg_user.chat_id, None)
                self.tg_client.send_message(chat_id=msg.chat.id, text="Чат с пользователем закрыт\n"
                                                                      "для продолжения напишите команду")
            else:
                self.tg_client.send_message(chat_id=msg.chat.id, text="Команда не найдена")
        elif tg_user.chat_id in self.data_client:
            client = self.data_client[tg_user.chat_id]
            client.next_handler(tg_user=tg_user, msg=msg, **client.data)
        else:
            self.tg_client.send_message(chat_id=msg.chat.id, text="Команда не найдена\n/goals\n/create\n/cancel")

    def goal_all(self, tg_user: TgUser, msg: Message) -> None:
        goals: list = [
            f"{goal.id} {goal.title}" for goal in Goal.objects.select_related("user").filter(
                user=tg_user.user, ).exclude(status=Goal.Status.archived)
        ]

        self.tg_client.send_message(chat_id=msg.chat.id, text="No goals" if not goals else "\n".join(goals))

    def goal_category_all(self, tg_user: TgUser, msg: Message) -> None:
        goal_category: list = [
            f"id: {goal_cat.id} name: {goal_cat.title}" for goal_cat in
            GoalCategory.objects.select_related(
                "user").filter(user=tg_user.user).exclude(is_deleted=True)]

        self.tg_client.send_message(chat_id=msg.chat.id, text="Выберите ID категории:")
        self.tg_client.send_message(chat_id=msg.chat.id,
                                    text="Категория отсутствует" if not goal_category else "\n".join(goal_category))

        self.data_client[tg_user.chat_id] = FSMData(next_handler=self._get_category)

    def _get_category(self, tg_user: TgUser, msg: Message) -> None:
        try:
            category = GoalCategory.objects.get(pk=msg.text)
        except GoalCategory.DoesNotExist:
            self.tg_client.send_message(chat_id=msg.chat.id, text="Категория отсутствует")
            return
        else:
            self.data_client[tg_user.chat_id] = FSMData(next_handler=self._create_goal, data={"category": category})
            self.tg_client.send_message(chat_id=msg.chat.id, text="Напишите название цели")

    def _create_goal(self, tg_user: TgUser, msg: Message, **kwargs: Any) -> None:
        category: list = kwargs["category"]
        Goal.objects.create(category=category, user=tg_user.user, title=msg.text)
        self.tg_client.send_message(chat_id=msg.chat.id, text="Цель создана")
