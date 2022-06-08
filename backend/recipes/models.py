from django.db import models
from colorfield.fields import ColorField
from users.models import CustomUser
from django.core.validators import MinValueValidator


class Tag(models.Model):
    name = models.CharField(verbose_name='Название тэга', max_length=144)
    color = ColorField(verbose_name='Цвет тега')
    slug = models.SlugField(verbose_name='Слаг')

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=144, verbose_name='Название ингридиента')
    unit = models.CharField(max_length=144, verbose_name='Единица измерения')

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, verbose_name='Автор', related_name='recipes')
    tags = models.ManyToManyField(Tag, verbose_name='Тэги', related_name='recipes')
    ingredients = models.ManyToManyField(Ingredient, verbose_name='Ингридиенты', related_name='recipes')
    name = models.CharField(max_length=200, verbose_name='Название рецепта')
    image = models.ImageField(verbose_name='Изображение рецепта')
    text = models.TextField(verbose_name='Текст рецепта')
    cooking_time = models.PositiveSmallIntegerField(verbose_name='Время приготавления', validators=[MinValueValidator(1)])

    def __str__(self):
        return self.name
