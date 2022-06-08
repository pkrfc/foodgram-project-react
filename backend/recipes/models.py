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
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='Автор', related_name='recipes')
    tags = models.ManyToManyField(Tag, verbose_name='Тэги', related_name='recipes')
    ingredients = models.ManyToManyField(Ingredient, verbose_name='Ингридиенты', related_name='recipes')
    name = models.CharField(max_length=200, verbose_name='Название рецепта')
    image = models.ImageField(verbose_name='Изображение рецепта')
    text = models.TextField(verbose_name='Текст рецепта')
    cooking_time = models.PositiveSmallIntegerField(verbose_name='Время приготавления', validators=[MinValueValidator(1)])
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class Purchase(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='purchase')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='purchase')

    class Meta:
        verbose_name = 'Покупка'
        verbose_name_plural = 'Покупки'

        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='Unique_recipe')
            ]

    def __str__(self):
        return f'В корзине {self.user} есть {self.recipe}'


class RecipeIngredients(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='recipe_ingredients',)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='recipe_ingredients')
    amount = models.PositiveSmallIntegerField(verbose_name='Количество ингридиентов', validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = 'Ингридиенты в рецепте'
        verbose_name_plural = 'Ингридиенты в рецепте'

    def __str__(self):
        return {self.ingredient}, {self.recipe}


class RecipeTags(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name='recipe_tags')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='recipe_tags')

    class Meta:
        verbose_name = 'Тэги в рецепте'
        verbose_name_plural = 'Тэги в рецепте'

    def __str__(self):
        return {self.tag}, {self.recipe}


class Favorite(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='favorite')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='favorite')

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self):
        return {self.user}, {self.recipe}

