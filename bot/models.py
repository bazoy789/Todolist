from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from core.models import User


# Create your models here.
class TgUser(models.Model):
    chat_id = models.BigIntegerField(unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    verification_code = models.CharField(max_length=50, null=True, blank=True)

    @staticmethod
    def gen_verification_code() -> str:
        return BaseUserManager().make_random_password()
