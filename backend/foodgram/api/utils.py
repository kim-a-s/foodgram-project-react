from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from .serializers import RecipeSerializer
from recipes.models import Recipe


def post_delete_fav_cart(self, request, pk, func_model):
    recipe = get_object_or_404(Recipe, id=pk)

    if request.method == 'POST':
        serializer = RecipeSerializer(recipe,
                                      data=request.data,
                                      context={
                                        "request": request
                                      }
        )
        serializer.is_valid(raise_exception=True)
        if not func_model.objects.filter(user=request.user,
                                         recipe=recipe).exists():
            func_model.objects.create(user=request.user,
                                      recipe=recipe)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        return Response({'errors': 'Рецепт уже в списке.'},
                         status=status.HTTP_400_BAD_REQUEST)

    get_object_or_404(func_model, user=request.user,
                      recipe=recipe).delete()
    return Response({'detail': 'Рецепт успешно удален из списка.'},
                     status=status.HTTP_204_NO_CONTENT)
