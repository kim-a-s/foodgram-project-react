from django.contrib.auth import get_user_model
from django.db.models.aggregates import Count, Sum
from django.db.models.expressions import Value
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (exceptions,
                            filters,
                            generics,
                            mixins,
                            permissions,
                            status,
                            viewsets,)
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import RecipeFilter
from .pagination import PagePagination
from .permissions import IsAuthorOrAdminPermission
from .serializers import (IngredientSerializer,
                          RecipeSerializer,
                          RecipeCreateSerializer,
                          SubscribeRecipeSerializer,
                          SubscriptionSerializer,
                          SubscriptionCreateSerializer,
                          TagSerializer,
                          UserCreateSerializer,
                          UserPasswordSerializer,
                          UserSerializer,)
from recipes.models import (Favorite,
                            Ingredient,
                            Recipe,
                            RecipeIngredient,
                            ShoppingСart,
                            Tag,)

User = get_user_model()

FILE_NAME = 'shopping_cart.txt'


class UserViewSet(mixins.CreateModelMixin,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):

    """Пользователи. Изменение пароля.
    Избранные авторы с рецептами.
    Подписка и отписка."""

    queryset = User.objects.all()
    pagination_class = PagePagination
    permission_classes = (permissions.AllowAny,)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve',):
            return UserSerializer
        return UserCreateSerializer

    @action(detail=False, methods=['get'],
            pagination_class=None,
            permission_classes=(permissions.IsAuthenticated,))
    def me(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'],
            permission_classes=(permissions.IsAuthenticated,))
    def set_password(self, request):
        serializer = UserPasswordSerializer(
            request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Пароль изменен!'},
                        status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=(permissions.IsAuthenticated,),
            pagination_class=PagePagination)
    def subscriptions(self, request):
        queryset = User.objects.filter(following__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(page,
                                            many=True,
                                            context={'request': request})
        return self.get_paginated_response(serializer.data)


class AddAndDeleteSubscribe(generics.RetrieveDestroyAPIView,
                            generics.ListCreateAPIView):
    """Подписка и отписка от пользователя."""

    serializer_class = SubscriptionCreateSerializer

    def get_queryset(self):
        return self.request.user.follower.select_related(
            'following'
        ).prefetch_related(
            'following__recipe'
        ).annotate(
            recipes_count=Count('following__recipe'),
            is_subscribed=Value(True), )

    def get_object(self):
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, id=user_id)
        self.check_object_permissions(self.request, user)
        return user

    def create(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.id == instance.id:
            return Response(
                {'errors': 'На самого себя не подписаться!'},
                status=status.HTTP_400_BAD_REQUEST)
        if request.user.follower.filter(author=instance).exists():
            return Response(
                {'errors': 'Уже подписан!'},
                status=status.HTTP_400_BAD_REQUEST)
        subs = request.user.follower.create(author=instance)
        serializer = self.get_serializer(subs)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        self.request.user.follower.filter(author=instance).delete()


class RecipeViewSet(viewsets.ModelViewSet):
    """"""
    queryset = Recipe.objects.all()
    filterset_class = RecipeFilter
    filter_backends = (DjangoFilterBackend,)
    pagination_class = PagePagination
    permission_classes = (IsAuthorOrAdminPermission,)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve',):
            return RecipeSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=('post', 'delete'))
    def favorite(self, request, pk=None):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if self.request.method == 'POST':
            if Favorite.objects.filter(user=user, recipe=recipe).exists():
                raise exceptions.ValidationError(
                    'Рецепт уже в избранном')

            Favorite.objects.create(user=user, recipe=recipe)
            serializer = SubscribeRecipeSerializer(
                recipe, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        favorite = get_object_or_404(Favorite, user=user, recipe=recipe)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=('post', 'delete'))
    def shopping_cart(self, request, pk=None):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        if self.request.method == 'POST':
            if ShoppingСart.objects.filter(user=user, recipe=recipe).exists():
                raise exceptions.ValidationError(
                    'Ингредиенты рецепта уже в списке покупок')

            ShoppingСart.objects.create(user=user, recipe=recipe)
            serializer = SubscribeRecipeSerializer(
                recipe, context={'request': request})

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if not ShoppingСart.objects.filter(user=user, recipe=recipe).exists():
            raise exceptions.ValidationError(
                'Рецептов нет в списке покупок')

        shopping_list = get_object_or_404(ShoppingСart,
                                          user=user,
                                          recipe=recipe)
        shopping_list.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=(permissions.IsAuthenticated,))
    def download_shopping_cart(self, request):
        ingredients = (
            RecipeIngredient.objects
            .filter(recipe__shopping_recipe__user=request.user)
            .values('ingredient')
            .annotate(total_amount=Sum('amount'))
            .values_list('ingredient__name', 'total_amount',
                         'ingredient__measurement_unit')
        )
        file_list = []
        [file_list.append(
            '{} - {} {}'.format(*ingredient)) for ingredient in ingredients]
        file = HttpResponse('Cписок покупок:\n' + '\n'.join(file_list),
                            content_type='text/plain')
        file['Content-Disposition'] = (f'attachment; filename={FILE_NAME}')
        return file


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)
    pagination_class = None


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
