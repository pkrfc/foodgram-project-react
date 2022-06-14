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


class CustomUserViewSet(UserViewSet):
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()

    @action(detail=True, methods=['POST', 'DELETE'], permission_classes=[IsAuthorOrReadOnly])
    def subscribe(self, request, id):
        user = request.user
        following = get_object_or_404(CustomUser, id=id)
        data = {'user': user.id, 'following': following.id}
        if request.method == 'POST':
            serializer = SubscribeSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            serializer = CustomUserSerializer(following)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        following = get_object_or_404(Subscribe, user=user.id, following=following.id)
        following.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['GET'], permission_classes=[IsAuthorOrReadOnly], url_name='subscriptions', url_path='subscriptions')
    def subscriptions(self, request):
        page = CustomUser.objects.filter(following__user=request.user)
        serializer = SubscriptionsSerializer(page, many=True)
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

    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return RecipeReadSerializer
        return RecipeSerializer

    @action(detail=True, methods=['POST'], permission_classes=[IsAuthenticated])
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

    @action(detail=True, methods=['POST'], permission_classes=[IsAuthenticated])
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


class SubscribeViewSet(ModelViewSet):
    serializer_class = SubscribeSerializer

    def get_queryset(self):
        return Subscribe.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        instance.delete()
