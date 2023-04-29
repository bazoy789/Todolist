from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    MAN = "man"
    WOMEN = "women"
    SEX = [(MAN, MAN), (WOMEN, WOMEN)]

    sex = models.CharField(max_length=6, choices=SEX, default=MAN)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["username"]
