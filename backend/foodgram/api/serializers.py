import base64

from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from rest_framework import serializers

from recipes.models import Tag, Recipe, Ingredient

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)
    

# class CustomUserCreateSerializer(UserCreateSerializer):
#     """Сериализатор для регистрации пользователей."""

#     class Meta:
#         model = User
#         fields = ('email', 'username', 'first_name', 'last_name', 'password')


class UserSerializer(serializers.ModelSerializer):
    """Список пользователей."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed',)

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return (
            user.is_authenticated and bool(obj.following.filter(user=user))
        )


class TagSerializer(serializers.ModelSerializer):
    """[GET] Список тегов."""

    class Meta:
        model = Tag
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'
