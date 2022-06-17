from django.contrib import admin

from .models import (Favorite, Ingredient, Purchase, Recipe, RecipeIngredients,
                     Tag)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    readonly_fields = ("slug",)
    fields = (
        "name",
        "color",
    )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    pass


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    pass


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    pass


@admin.register(RecipeIngredients)
class RecipeIngredientsAdmin(admin.ModelAdmin):
    pass


@admin.register(Recipe)
class RecipesAdmin(admin.ModelAdmin):
    list_display = ('author', 'name', 'favorite_count')
    list_filter = ('name', 'author', 'tags')
    empty_value_display = "-пусто-"

    def favorite_count(self, obj):
        return Favorite.objects.filter(recipe=obj).count()
