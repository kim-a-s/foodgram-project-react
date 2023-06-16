from distutils.util import strtobool

from django_filters import rest_framework

from recipes import models

OPTIONS = (
    ('0', 'False'),
    ('1', 'True')
)


class RecipeFilter(rest_framework.FilterSet):
    author = rest_framework.NumberFilter(
        field_name='author',
        lookup_expr='exact'
    )
    tags = rest_framework.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=models.Tag.objects.all(),
        to_field_name='slug',
    )
    is_favorited = rest_framework.ChoiceFilter(
        choices=OPTIONS,
        method='is_favorited_method'
    )
    is_in_shopping_cart = rest_framework.ChoiceFilter(
        choices=OPTIONS,
        method='is_in_shopping_cart_method'
    )

    def is_favorited_method(self, queryset, name, value):
        if self.request.user.is_anonymous:
            return models.Recipe.objects.none()

        favorites = models.Favorite.objects.filter(user=self.request.user)
        recipes = [item.recipe.id for item in favorites]
        new_queryset = queryset.filter(id__in=recipes)

        if not strtobool(value):
            return queryset.difference(new_queryset)
        return queryset.filter(id__in=recipes)

    def is_in_shopping_cart_method(self, queryset, name, value):
        if self.request.user.is_anonymous:
            return models.Recipe.objects.none()

        shopping_cart = models.ShoppingСart.objects.filter(user=self.request.user)
        recipes = [item.recipe.id for item in shopping_cart]
        new_queryset = queryset.filter(id__in=recipes)

        if not strtobool(value):
            return queryset.difference(new_queryset)
        return queryset.filter(id__in=recipes)

    class Meta:
        model = models.Recipe
        fields = ('tags', 'author')
