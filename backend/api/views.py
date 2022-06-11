from djoser.views import UserViewSet
from .serializers import SingUpSerializer, TagSerializer, SubscribeSerializer, IngredientSerializer, RecipeIngredientsSerializer, RecipeSerializer, CustomUserSerializer, RecipeReadSerializer
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from users.models import CustomUser, Subscribe
from recipes.models import Tag, Ingredient, Recipe, RecipeIngredients, Favorite, Purchase
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend


class CustomUserViewSet(UserViewSet):
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class SubscribeViewSet(ModelViewSet):
    serializer_class = SubscribeSerializer

    def get_queryset(self):
        return Subscribe.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        instance.delete()


class IngredientViewSet(ModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('^name',)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return RecipeReadSerializer
        return RecipeSerializer


