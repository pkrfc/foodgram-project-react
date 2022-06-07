from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'password', 'first_name', 'last_name']

    email = models.EmailField(max_length=254, unique=True, db_index=True)

    def __str__(self):
        return self.username
