from django.contrib import admin
from django.urls import path, include

from .views import *

urlpatterns = [
    path('recipes/', recipes),
    path('recipes/<int:recipes_id>/', recipe_detail),
    path('tags/', tags),
]