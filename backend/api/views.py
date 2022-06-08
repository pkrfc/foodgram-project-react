from djoser.views import UserViewSet
from .serializers import SingUpSerializer, TagSerializer
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from users.models import CustomUser
from recipes.models import Tag


class CustomUserViewSet(UserViewSet):
    serializer_class = SingUpSerializer
    queryset = CustomUser.objects.all()


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
