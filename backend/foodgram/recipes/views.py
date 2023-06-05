from django.shortcuts import render
from django.http import HttpResponse

def recipes(request):
    return HttpResponse("List of recipes")

def recipe_detail(request):
    return HttpResponse("Recipe_detail")

def tags(request):
    return HttpResponse("Tags")
