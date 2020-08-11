import json
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django import forms
from django.core.paginator import Paginator

from .models import User, Recipe, Comment


class CommentForm(forms.Form):
    comment_content = forms.CharField(label = "", widget=forms.Textarea(attrs={'placeholder': 'Post a comment (256 chars max)', 'style': 'width: 600px; height: 180px'}))

class RecipeForm(forms.Form):
    recipe_title = forms.CharField(widget=forms.TextInput(attrs={'help_text': 'Listing name'}))
    recipe_description = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Short recipe description', 'style': 'width: 500px'}))
    recipe_ingredients = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Recipe Ingredients', 'style': 'width: 500px'}))
    recipe_directions = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Recipe Directions', 'style': 'width: 500px'}))
    recipe_img = forms.ImageField()


def index(request):
    return render(request, "main/index.html") 


def about(request):
    return render(request, "main/about.html") 


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "main/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "main/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "main/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "main/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "main/register.html")


def recipes(request):
    return render(request, "main/recipes.html", {
        'recipes': Recipe.objects.all()
    })


def recipe_view(request, id):
    return render(request, "main/recipe.html", {
        'recipe': Recipe.objects.get(id=id),
        'comment_form': CommentForm(),
        'comments': Comment.objects.filter(recipe=id)
    })


@login_required
def comment(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    data = json.loads(request.body)   

    comment_body = data.get("comment", "")
    recipe_id = data.get("recipe", "")

    try:
        new_comment = Comment(user=request.user, comment = comment_body, recipe = Recipe.objects.get(id=recipe_id))
        new_comment.save()
        return JsonResponse({"message": "Comment successfully added!", "status": 201, "created_at": f"{new_comment.created_at}", "user": f"{request.user}"}, status=201)
    except:
        return JsonResponse({"message": f"{recipe_id}"}, status=403)


@login_required
def create(request):
    return render(request, "main/create.html", {
        'form': RecipeForm()
    })
    