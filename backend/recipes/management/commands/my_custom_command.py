import json

from recipes.models import Ingredient
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open(
                'data/ingredients.json', encoding='utf-8'
        ) as json_file:
            ingredients = json.load(json_file)
            for ingredient in ingredients:
                name = ingredient['name']
                measurement_unit = ingredient['measurement_unit']
                Ingredient.objects.create(
                    name=name,
                    measurement_unit=measurement_unit
                )


app = Command()
app.handle()
print('Загрузка оконченна')
