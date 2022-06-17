from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import F, Q


class CustomUser(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'password', 'first_name', 'last_name']

    email = models.EmailField(max_length=254, unique=True, db_index=True)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='followers',
    )
    following = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'

        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'], name='Unique_follow'),
            models.CheckConstraint(
                check=~Q(user=F('following')), name='Check_follow')
        ]

    def __str__(self):
        return {self.user}, {self.following}
