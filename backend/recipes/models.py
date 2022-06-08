from django.db import models
from colorfield.fields import ColorField
from users.models import CustomUser
from django.core.validators import MinValueValidator


class Tag(models.Model):
    name = models.CharField(max_length=144)
    color = ColorField()
    slug = models.SlugField

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=144)
    unit = models.CharField(max_length=144)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag)
    ingredients = models.ManyToManyField(Ingredient)
    name = models.CharField(max_length=200)
    image = models.ImageField()
    text = models.TextField()
    cooking_time = models.PositiveSmallIntegerField(validators=[MinValueValidator(0)])

    def __str__(self):
        return self.name
