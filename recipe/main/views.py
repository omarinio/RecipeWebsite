import json
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django import forms
from django.core.paginator import Paginator

from .models import User, Recipe, Comment, Follow, Like


class CommentForm(forms.Form):
    comment_content = forms.CharField(label = "", widget=forms.Textarea(attrs={'placeholder': 'Post a comment (256 chars max)', 'style': 'width: 600px; height: 180px'}))

class RecipeForm(forms.Form):
    recipe_title = forms.CharField(widget=forms.TextInput(attrs={'style': 'width: 500px'}))
    recipe_description = forms.CharField(widget=forms.Textarea(attrs={'style': 'width: 500px'}))
    recipe_ingredients = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Seperate ingredients with commas', 'style': 'width: 500px'}))
    recipe_directions = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Number each step and put it on its own line', 'style': 'width: 500px'}))
    recipe_img = forms.ImageField(required=False)

class SearchForm(forms.Form):
    search_form = forms.CharField(label='', widget=forms.TextInput(attrs={'placeholder': 'Search', 'class': "form-control mr-sm-2"}))


def index(request):
    random_recipe = Recipe.objects.order_by('?').first()

    print(random_recipe)

    return render(request, "main/index.html", {
        "recipe": random_recipe,
        "search": SearchForm()
    }) 


def about(request):
    return render(request, "main/about.html", {
        "search": SearchForm()
    }) 


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
                "message": "Invalid username and/or password.",
                "search": SearchForm()
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
                "message": "Passwords must match.",
                "search": SearchForm()
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "main/register.html", {
                "message": "Username already taken.",
                "search": SearchForm()
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "main/register.html", {
            "search": SearchForm()
        })


def recipes(request):
    user_recipes = Recipe.objects.all()

    # user_posts = Post.objects.filter(user = user_profile).order_by('-timestamp')

    paginated_recipes = Paginator(user_recipes, 12)

    page_number = request.GET.get('page')
    page_recipes = paginated_recipes.get_page(page_number)

    return render(request, "main/recipes.html", {
        'recipes': page_recipes,
        "search": SearchForm()
    })


def recipe_view(request, id):
    recipe = Recipe.objects.get(id=id)
    ingredients = recipe.ingredients.split(",")

    can_delete = False
    
    if request.user == recipe.user:
        can_delete = True

    return render(request, "main/recipe.html", {
        'recipe': recipe,
        'comment_form': CommentForm(),
        'comments': Comment.objects.filter(recipe=id),
        'ingredients': ingredients,
        "search": SearchForm(),
        "can_delete": can_delete
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
    if request.method == "POST":
        new_recipe = RecipeForm(request.POST, request.FILES)

        if new_recipe.is_valid():
            new_recipe_title = new_recipe.cleaned_data["recipe_title"]
            new_recipe_description = new_recipe.cleaned_data["recipe_description"]
            new_recipe_ingredients = new_recipe.cleaned_data["recipe_ingredients"]
            new_recipe_directions = new_recipe.cleaned_data["recipe_directions"]
            new_recipe_img = new_recipe.cleaned_data["recipe_img"]

            new_recipe_object = Recipe.objects.create(user = request.user, title = new_recipe_title, description = new_recipe_description, ingredients = new_recipe_ingredients,
                                        body = new_recipe_directions, picture = new_recipe_img)

            new_recipe_object.save()

            return HttpResponseRedirect(reverse("index"))
        else:
            print(new_recipe.errors)

    return render(request, "main/create.html", {
        'form': RecipeForm(),
        "search": SearchForm()
    })


def user(request, username):

    user_profile = User.objects.get(username=username)

    followers = Follow.objects.filter(user = user_profile).count
    following = Follow.objects.filter(follower = user_profile).count

    user_recipes = Recipe.objects.filter(user = user_profile)

    # user_posts = Post.objects.filter(user = user_profile).order_by('-timestamp')

    paginated_recipes = Paginator(user_recipes, 12)

    page_number = request.GET.get('page')
    page_recipes = paginated_recipes.get_page(page_number)

    if request.user.is_authenticated and request.user != user_profile:
        is_following = False

        if Follow.objects.filter(user = user_profile, follower = request.user).count() > 0:
            is_following = True

        return render(request, "main/profile.html", {
            "user_profile": user_profile,
            "followers": followers,
            "following": following,
            "can_follow": True,
            "is_following": is_following,
            "recipes": page_recipes,
            "search": SearchForm()
        })
    else:
        return render(request, "main/profile.html", {
            "user_profile": user_profile,
            "followers": followers,
            "following": following,
            "can_follow": False,
            "recipes": page_recipes,
            "search": SearchForm()
        })


@login_required(login_url='login')
def follow(request):
    if request.method == "POST":
        data = json.loads(request.body)

        user = data.get("user", "")
        action = data.get("action", "")

        if action == "Follow":
            try:
                if Follow.objects.filter(user = User.objects.get(username = user), follower = request.user).count() == 0:
                    Follow.objects.create(user = User.objects.get(username = user), follower = request.user)
                    
                    return JsonResponse({'status': 201, 'action': "Unfollow", 'followers': Follow.objects.filter(user = User.objects.get(username = user)).count()}, status=201)
                else:
                    return JsonResponse({'message': "You are already following this user!"}, status=400)
            except:
                return JsonResponse({}, status=404)
        else:
            try:
                if Follow.objects.filter(user = User.objects.get(username = user), follower = request.user).count() > 0:
                    follow_to_delete = Follow.objects.get(user = User.objects.get(username = user), follower = request.user)
                    follow_to_delete.delete()

                    return JsonResponse({'status': 201, 'action': "Follow", 'followers': Follow.objects.filter(user = User.objects.get(username = user)).count()}, status=201)
                else: 
                    return JsonResponse({'message': "You cannot unfollow a user you are not following!"}, status=400)
            except:
                return JsonResponse({}, status=404)

    return JsonResponse({}, status=400)


@login_required
def view_liked(request):
    liked_recipes = Like.objects.filter(user = request.user)
    return render(request, "main/liked_recipes.html", {
            "recipes": liked_recipes,
            "search": SearchForm()
        })


@login_required
def like_recipe(request):
    if request.method != "PUT":
        return JsonResponse({"status": 400, 'message': "Must access through PUT request"}, status = 400)

    data = json.loads(request.body)

    post_id = data.get("post_id", "")
    action = data.get("action", "")
    
    try:       
        recipe = Recipe.objects.get(id = post_id)
    except:
        return JsonResponse({"status": 404, 'message': "Post not found"}, status = 404)

    if action == "like":
        try:
            if request.user in recipe.likes.all():
                return JsonResponse({"status": 400, 'message': "You already liked this post!"}, status=400)
            else:
                recipe.likes.add(request.user)
                recipe.save()
                Like.objects.create(user = request.user, recipe = recipe)
                return JsonResponse({"status": 201}, status = 201)
        except:
            return JsonResponse({"status": 400, 'message': "Something has gone wrong..."}, status=400)
    else:
        try:
            if request.user in recipe.likes.all():
                recipe.likes.remove(request.user)
                recipe.save()
                liked = Like.objects.get(user = request.user, recipe = recipe)
                liked.delete()
                return JsonResponse({"status": 201}, status = 201)
            else:
                return JsonResponse({"status": 400, 'message': "You cannot unlike a post you haven't liked!"}, status=400)
        except:
            return JsonResponse({"status": 400, 'message': "Something has gone wrong..."}, status=400)

    
def search(request):

    if request.method == "POST":

        form = SearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data["search_form"]

            substring_recipes = [s for s in Recipe.objects.values_list('title', flat=True) if query in s.lower()]
            substring_users = [s for s in User.objects.values_list('username', flat=True) if query in s.lower()]

            recipes = Recipe.objects.filter(title__in=substring_recipes)
            users = User.objects.filter(username__in=substring_users)

            return render(request, "main/search.html", {
                    "recipes": recipes,
                    "users": users,
                    "search": SearchForm()
                })


@login_required
def delete(request, id):
    if request.method == "POST":

        recipe = Recipe.objects.get(id=id)

        if request.user != recipe.user:
            return render(request, "main/error.html", {
                "message": "You do not have permission to delete that."
            })
        
        recipe.delete()
        return redirect('/')

    return render(request, "main/error.html", {
                "message": "You do not have permission to delete that."
            })
    

@login_required
def edit_recipe(request, id):
    if request.method == "POST":

        form = RecipeForm(request.POST, request.FILES)

        if form.is_valid():
            edit_title = form.cleaned_data["recipe_title"]
            edit_description = form.cleaned_data["recipe_description"]
            edit_ingredients = form.cleaned_data["recipe_ingredients"]
            edit_directions = form.cleaned_data["recipe_directions"]
            # edit_img = form.cleaned_data["recipe_img"]

            recipe_set = Recipe.objects.filter(id=id)

            recipe_set.update(title = edit_title, description = edit_description, ingredients = edit_ingredients,
                                        body = edit_directions)

            recipe = recipe_set.first()

            recipe.save()

            ingredients = recipe.ingredients.split(",")

            can_delete = False
            
            if request.user == recipe.user:
                can_delete = True

            return render(request, "main/recipe.html", {
                'recipe': recipe,
                'comment_form': CommentForm(),
                'comments': Comment.objects.filter(recipe=id),
                'ingredients': ingredients,
                "search": SearchForm(),
                "can_delete": can_delete
            })
        
        else:
            print(form.errors)
            return render(request, "main/error.html", {
                "message": "Error submitting form, please try again."
            })

    # when you open up edit page
    try:
        recipe = Recipe.objects.get(id=id)
        if request.user == recipe.user:
            return render(request, "main/edit.html", {
                'form': RecipeForm(initial={
                    "recipe_title": recipe.title,
                    "recipe_description": recipe.description,
                    "recipe_ingredients": recipe.ingredients,
                    "recipe_directions": recipe.body
                }),
                "search": SearchForm(),
                "recipe": recipe
            })
        else:
            return render(request, "main/error.html", {
                "message": "You do not have permission to access that."
            })
    except:
        return render(request, "main/error.html", {
            "message": "You do not have permission to access that."
        })