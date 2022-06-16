from rest_framework import serializers
from djoser.serializers import UserCreateSerializer, UserSerializer
from users.models import CustomUser, Subscribe
from rest_framework.relations import SlugRelatedField
from recipes.models import Ingredient, Tag, Recipe, RecipeIngredients, Favorite, Purchase
from drf_extra_fields.fields import Base64ImageField
from rest_framework.validators import UniqueTogetherValidator


class SingUpSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = CustomUser
        fields = ('id', 'username', 'email', 'first_name',
                  'last_name', 'password')


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Subscribe.objects.filter(following=obj.id, user=request.user).exists()


class SubscriptionsSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count'
                  )

    def get_recipes(self, obj):
        return RecipeInfoSerializer(obj.recipes.all(), many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()


class SubscribeSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    following = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())

    class Meta:
        model = Subscribe
        fields = '__all__'

        validators = [
            UniqueTogetherValidator(
                queryset=Subscribe.objects.all(),
                fields=('user', 'following'),
                message='Вы уже подписаны на этого пользователя'
            )
        ]

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Subscribe.objects.filter(following=obj.id, user=request.user).exists()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientsSerializer(many=True, read_only=True, source='ingredients.amount_set',)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited', 'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time')

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user is None or user.is_anonymous:
            return False
        return Favorite.objects.filter(recipe=obj, user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user is None or user.is_anonymous:
            return False
        return Purchase.objects.filter(recipe=obj, user=user).exists()

    def create(self, validated_data):
        request = self.context.get('request')
        image = validated_data.pop('image')
        ingredients_data = self.initial_data.get('ingredients')
        recipe = Recipe.objects.create(author=request.user, image=image, **validated_data)
        tags_data = self.initial_data.get('tags')
        recipe.tags.set(tags_data)
        for ingredient in ingredients_data:
            RecipeIngredients.objects.create(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount'),
            )
        return recipe

    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time)
        instance.tags.clear()
        tags_data = self.initial_data.get('tags')
        instance.tags.set(tags_data)
        RecipeIngredients.objects.filter(recipe=instance).all().delete()
        ingredients_data = self.initial_data.get('ingredients')
        for ingredient in ingredients_data:
            RecipeIngredients.objects.create(
                recipe=instance,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount'),
            )
        instance.save()
        return instance


class RecipeReadSerializer(RecipeSerializer):
    tags = TagSerializer(read_only=True, many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()

    def get_ingredients(self, obj):
        ingredients = RecipeIngredients.objects.filter(recipe=obj)
        return RecipeIngredientsSerializer(ingredients, many=True).data


class PurchaseSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = Purchase
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Purchase.objects.all(),
                fields=('user', 'recipe'),
                message='Этот рецепт уже в корзине'
            )
        ]


class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = Favorite
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Этот рецепт уже в избранном'
            )
        ]


class RecipeInfoSerializer(RecipeSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
