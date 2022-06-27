import django_filters as filters
from rest_framework.filters import SearchFilter
from recipes.models import Recipe, Tag


class IngredientSearchFilter(SearchFilter):
    search_param = 'name'


class RecipeFilter(filters.FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name="tags__slug",
        queryset=Tag.objects.all(),
        to_field_name="slug",
    )

    is_favorited = filters.BooleanFilter(
        method='get_is_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart',)

    def get_is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(favorite__user=self.request.user)
        return Recipe.objects.all()

    def get_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(purchase__user=self.request.user)
        return Recipe.objects.all()
