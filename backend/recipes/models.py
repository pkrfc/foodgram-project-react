from colorfield.fields import ColorField
from django.core.validators import MinValueValidator
from django.db import models
from users.models import CustomUser


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
    name = models.CharField(
        max_length=144,
        verbose_name='Название ингридиента'
    )
    measurement_unit = models.CharField(
        max_length=144, verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='recipes',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингридиенты',
        related_name='recipes',
        through='RecipeIngredient')
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта'
    )
    image = models.ImageField(
        upload_to='recipes/image/',
        verbose_name='Изображение рецепта'
    )
    text = models.TextField(
        verbose_name='Текст рецепта'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготавления',
        validators=[MinValueValidator(1)]
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество ингридиентов',
        validators=[MinValueValidator(1)]
    )

    class Meta:
        verbose_name = 'Ингридиенты в рецепте'
        verbose_name_plural = 'Ингридиенты в рецепте'

        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'], name='Unique_ingredient')
        ]

    def __str__(self):
        return f'{self.ingredient}, {self.recipe}'


class Purchase(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='purchase'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='purchase'
    )

    class Meta:
        verbose_name = 'Покупка'
        verbose_name_plural = 'Покупки'

        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='Unique_recipe')
        ]

    def __str__(self):
        return f'В корзине {self.user} есть {self.recipe}'


class Favorite(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='favorite'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite'
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'

        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='Unique_favorite')
        ]

    def __str__(self):
        return f'{self.user}, {self.recipe}'
