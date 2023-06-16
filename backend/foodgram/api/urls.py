from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (IngredientViewSet,
                    RecipeViewSet,
                    TagViewSet,
                    UserViewSet,
                    AddAndDeleteSubscribe,)

router = DefaultRouter()

router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)
router.register('users', UserViewSet)

urlpatterns = [
    path('users/<int:user_id>/subscribe/', AddAndDeleteSubscribe.as_view(),
         name='subscribe'),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
