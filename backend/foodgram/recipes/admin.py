from django.contrib import admin

from .models import Recipe, Ingredient, Tag, Recipe_ingredient
from . import models


admin.site.register(Recipe)
admin.site.register(Ingredient)
admin.site.register(Tag)
admin.site.register(Recipe_ingredient)
