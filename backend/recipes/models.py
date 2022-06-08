from django.db import models
from colorfield.fields import ColorField


class Tag(models.Model):
    name = models.CharField(max_length=144)
    color = ColorField()
    slug = models.SlugField

    def __str__(self):
        return self.name