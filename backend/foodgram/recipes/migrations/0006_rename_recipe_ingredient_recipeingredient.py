# Generated by Django 3.2.19 on 2023-06-06 09:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_auto_20230530_1915'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Recipe_ingredient',
            new_name='RecipeIngredient',
        ),
    ]
