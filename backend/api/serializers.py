from rest_framework import serializers
from djoser.serializers import UserCreateSerializer
from users.models import CustomUser
from recipes.models import Tag


class SingUpSerializer(UserCreateSerializer):

    class Meta(UserCreateSerializer.Meta):
        model = CustomUser
        fields = ('id', 'username', 'email', 'first_name',
                  'last_name', 'password')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']
