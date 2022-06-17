from djoser.views import UserViewSet
from .serializers import SingUpSerializer, TagSerializer, SubscribeSerializer, IngredientSerializer, \
    RecipeIngredientsSerializer, RecipeSerializer, CustomUserSerializer, RecipeReadSerializer, PurchaseSerializer, \
    RecipeInfoSerializer, FavoriteSerializer, SubscriptionsSerializer
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from users.models import CustomUser, Subscribe
from recipes.models import Tag, Ingredient, Recipe, RecipeIngredients, Favorite, Purchase
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from .permissions import IsAuthorOrReadOnly
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from .filters import RecipeFilter
from django.http.response import HttpResponse


class CustomUserViewSet(UserViewSet):
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()

    @action(detail=True, methods=['POST', 'DELETE'], permission_classes=[IsAuthenticated])
    def subscribe(self, request, id):
        user = request.user
        following = get_object_or_404(CustomUser, id=id)
        data = {'user': user.id, 'following': following.id}
        if request.method == 'POST':
            serializer = SubscribeSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            serializer = CustomUserSerializer(following, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        following = get_object_or_404(Subscribe, user=user.id, following=following.id)
        following.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['GET'], permission_classes=[IsAuthenticated], url_name='subscriptions', url_path='subscriptions')
    def subscriptions(self, request):
        page = CustomUser.objects.filter(following__user=request.user)
        serializer = SubscriptionsSerializer(page, many=True, context={'request': request})
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

    @action(detail=True, methods=['POST'], permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk=None):
        user = request.user
        recipe = self.get_object()
        data = {'user': user.id, 'recipe': recipe.id}
        serializer = PurchaseSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        serializer = RecipeInfoSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        user = request.user
        recipe = self.get_object()
        cart = get_object_or_404(Purchase, user=user, recipe=recipe)
        cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['POST'], permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk=None):
        user = request.user
        recipe = self.get_object()
        data = {'user': user.id, 'recipe': recipe.id}
        serializer = FavoriteSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        serializer = RecipeInfoSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        user = request.user
        recipe = self.get_object()
        favorite = get_object_or_404(Favorite, user=user, recipe=recipe)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['GET'], permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request, pk=None):
        file = {}
        ingredients = RecipeIngredients.objects.filter(
            recipe__purchase__user=request.user
        )
        for ingredient in ingredients:
            name = ingredient.ingredient.name
            measurement_unit = ingredient.ingredient.measurement_unit
            amount = ingredient.amount
            if name not in file:
                file[name] = {
                    'measurement_unit': measurement_unit,
                    'amount': amount
                }
            else:
                file[name]['amount'] += amount
        ingredient_list = []
        for item, value in file.items():
            ingredient_list.append(f"{item}: {value['amount']} {value['measurement_unit']} \n")
        ingredient_list.append('\nСпасибо, что воспользовались нашим сервисом!')
        response = HttpResponse(ingredient_list, 'Content-Type: text/plain')
        response['Content-Disposition'] = 'attachment; filename="ingredient_list.txt"'
        return response
