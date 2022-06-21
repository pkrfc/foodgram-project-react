from django.db import transaction
from django.db.models import Sum
from django.http.response import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from recipes.models import (Favorite, Ingredient, Purchase, Recipe,
                            RecipeIngredient, Tag)
from users.models import CustomUser, Subscribe
from .filters import RecipeFilter
from .permissions import IsAuthorOrReadOnly
from .serializers import (CustomUserSerializer, IngredientSerializer,
                          RecipeInfoSerializer, RecipeReadSerializer,
                          RecipeSerializer, SubscribeSerializer,
                          SubscriptionsSerializer, TagSerializer)


class CustomUserViewSet(UserViewSet):
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()

    @transaction.atomic
    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id):
        user = request.user
        following = get_object_or_404(CustomUser, id=id)
        data = {'user': user.id, 'following': following.id}
        if request.method == 'POST':
            serializer = SubscribeSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            serializer = CustomUserSerializer(
                following,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        following = get_object_or_404(
            Subscribe,
            user=user.id,
            following=following.id
        )
        following.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[IsAuthenticated],
        url_name='subscriptions',
        url_path='subscriptions'
    )
    def subscriptions(self, request):
        page = CustomUser.objects.filter(following__user=request.user)
        serializer = SubscriptionsSerializer(
            page, many=True,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(ModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('^name',)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filter_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return RecipeReadSerializer
        return RecipeSerializer

    @action(
        detail=True,
        methods=['POST'],
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk=None):
        return self.add_obj(Purchase, request.user, pk)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        return self.delete_obj(Purchase, request.user, pk)

    @action(
        detail=True,
        methods=['POST'],
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        return self.add_obj(Favorite, request.user, pk)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        return self.delete_obj(Favorite, request.user, pk)

    @transaction.atomic
    def add_obj(self, model, user, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = RecipeInfoSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @transaction.atomic
    def delete_obj(self, model, user, pk):
        obj = model.objects.filter(user=user, recipe=pk)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__purchase__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(
            total=Sum('amount')
        )
        ingredient_list = []
        for ingredient in ingredients:
            line = f'{ingredient["ingredient__name"]}:{ingredient["total"]} \n'
            f'{ingredient["ingredient__measurement_unit"]}'
            ingredient_list.append(line)
        ingredient_list.append('\nСпасибо, что Вы с нами!')
        response = HttpResponse(ingredient_list, 'Content-Type: text/plain')
        response['Content-Disposition'] = 'attachment; filename="ingredient_list.txt"'
        return response
