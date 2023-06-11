from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from . import serializers
from recipes import models
from .filters import RecipeFilter
from .pagination import PagePagination

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
            return serializers.UserSerializer
        return serializers.UserCreateSerializer
    
    @action(detail=False, methods=['get'],
            pagination_class=None,
            permission_classes=(permissions.IsAuthenticated,))
    def me(self, request):
        serializer = serializers.UserSerializer(request.user)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'],
            permission_classes=(permissions.IsAuthenticated,))
    def set_password(self, request):
        serializer = serializers.UserPasswordSerializer(
            request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'detail': 'Пароль изменен!'},
                            status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'Введите верные данные!'},
            status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'],
            permission_classes=(permissions.IsAuthenticated,),
            pagination_class=PagePagination)
    def subscriptions(self, request):
        queryset = User.objects.filter(subscribing__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = serializers.SubscriptionSerializer(page, many=True,
                                             context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(permissions.IsAuthenticated,))
    def subscribe(self, request, **kwargs):
        author = get_object_or_404(User, id=kwargs['pk'])

        if request.method == 'POST':
            serializer = serializers.SubscriptionCreateSerializer(
                author, data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            models.Subscription.objects.create(user=request.user, author=author)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            get_object_or_404(models.Subscription, user=request.user,
                              author=author).delete()
            return Response({'detail': 'Вы отписались от автора'},
                            status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = models.Recipe.objects.all()
    pagination_class = PagePagination
    filter_backends = [filters.OrderingFilter, filters.SearchFilter, DjangoFilterBackend]
    filterset_class = RecipeFilter
    ordering_fields = ['-pub_date']
    search_fields = ['tags']

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve',):
            return serializers.RecipeSerializer
        return serializers.RecipeCreateSerializer
    
    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(permissions.IsAuthenticated,))
    def favorite(self, request, **kwargs):
        recipe = get_object_or_404(models.Recipe, id=kwargs['pk'])

        if request.method == 'POST':
            serializer = serializers.RecipeSerializer(recipe, data=request.data,
                                                      context={"request": request})
            serializer.is_valid(raise_exception=True)
            if not models.Favorite.objects.filter(user=request.user,
                                                  recipe=recipe).exists():
                models.Favorite.objects.create(user=request.user, recipe=recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response({'errors': 'Рецепт уже в избранном.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            get_object_or_404(models.Favorite, user=request.user,
                              recipe=recipe).delete()
            return Response({'detail': 'Рецепт успешно удален из избранного.'},
                            status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(permissions.IsAuthenticated,))
    def shopping_cart(self, request, **kwargs):
        recipe = get_object_or_404(models.Recipe, id=kwargs['pk'])

        if request.method == 'POST':
            serializer = serializers.RecipeSerializer(recipe, data=request.data,
                                                      context={"request": request})
            serializer.is_valid(raise_exception=True)
            if not models.Shopping_cart.objects.filter(user=request.user,
                                                recipe=recipe).exists():
                models.Shopping_cart.objects.create(user=request.user, recipe=recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response({'errors': 'Рецепт уже в списке покупок.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            get_object_or_404(models.Shopping_cart, user=request.user,
                              recipe=recipe).delete()
            return Response(
                {'detail': 'Рецепт успешно удален из списка покупок.'},
                status=status.HTTP_204_NO_CONTENT
            )

    @action(detail=False, methods=['get'],
            permission_classes=(permissions.IsAuthenticated,))
    def download_shopping_cart(self, request):
        ingredients = (
            models.RecipeIngredient.objects
            .filter(recipe__shopping_recipe__user=request.user)
            .values('ingredient')
            .annotate(total_amount=Sum('amount'))
            .values_list('ingredient__name', 'total_amount',
                         'ingredient__measurement_unit')
        )
        file_list = []
        [file_list.append(
            '{} - {} {}.'.format(*ingredient)) for ingredient in ingredients]
        file = HttpResponse('Cписок покупок:\n' + '\n'.join(file_list),
                            content_type='text/plain')
        file['Content-Disposition'] = (f'attachment; filename={FILE_NAME}')
        return file


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['^name', 'name']
