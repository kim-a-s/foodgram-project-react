# Generated by Django 3.2.19 on 2023-06-11 18:48

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0006_rename_recipe_ingredient_recipeingredient'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Shopping_cart',
            new_name='ShoppingСart',
        ),
    ]
