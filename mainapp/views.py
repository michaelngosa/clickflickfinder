from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from .forms import *
from django.contrib.auth.forms import UserCreationForm
import requests
from django.http import HttpResponse
from django.http.response import JsonResponse
from .models import Comment
from django.contrib.auth.models import User

# Create your views here.
TMDB_API_KEY = "6b58ed600bc1ca6b0964c9d4685d7ed9"

@login_required
def dashboard(request): #Main screen
     return render(request, 'registration/dashboard.html')

def register(request):
     if request.method == 'POST':
          user_form = UserRegisterationForm(request.POST)
          if user_form.is_valid():
               #Create a new user object but avoid saving it yet
               new_user = user_form.save(commit=False)
               #set the choosen password
               new_user.set_password(
                    user_form.cleaned_data['password']
               )
               #Save the user object
               new_user.save()
               return render(request, 'registration/register_done.html', {'new_user': new_user})
     
     else:
          user_form = UserRegisterationForm()
     return render(request, 'registration/register.html', {'user_form': user_form} )

def search(request):

    # Get the query from the search box
    query = request.GET.get('q')
    type = request.GET.get("type")
    print(query)
    
    # If the query is not empty
    if query:

        # Get the results from the API
        data = requests.get(f"https://api.themoviedb.org/3/search/{request.GET.get('type')}?api_key={TMDB_API_KEY}&language=en-US&page=1&include_adult=false&query={query}")
        print(data.json())        
        
    else:
        return HttpResponse("Please enter a search query")
        
    # Render the template
    return render(request, 'registration/results.html', {
        "data": data.json(),
        "type": request.GET.get("type")
    })
    
def view_tv_detail(request, tv_id):
     data = requests.get(f"https://api.themoviedb.org/3/tv/{tv_id}?api_key={TMDB_API_KEY}&language=en-US")
     recommendations = requests.get(f"https://api.themoviedb.org/3/tv/{tv_id}/recommendations?api_key={TMDB_API_KEY}&language=en-US")
     return render(request, "registration/tv_detail.html", {
          "data": data.json(),
           "recommendations": recommendations.json(),
           "type": "tv",
    })

def view_movie_detail(request, movie_id):
     data = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US")
     recommendations = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}/recommendations?api_key={TMDB_API_KEY}&language=en-US")
     return render(request, "registration/movie_detail.html", {
          "data": data.json(),
          "recommendations": recommendations.json(),
          "type": "movie",
    })

def view_trendings_results(request):
    type = request.GET.get("media_type")
    time_window = request.GET.get("time_window")

    trendings = requests.get(f"https://api.themoviedb.org/3/trending/{type}/{time_window}?api_key={TMDB_API_KEY}&language=en-US")
    return JsonResponse(trendings.json())

def comment_page(request, movie_id):
    if request.method == "POST":
        user = request.user
        comment = request.POST.get("comment")

        if not request.user.is_authenticated:
            user = User.objects.get(id=1)

        Comment(comment=comment, user=user, movie_id=movie_id).save()

        return redirect(f"/movie/{movie_id}/comments/")

    else:
        data = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US")
        title = data.json()["title"]

        comments = reversed(Comment.objects.filter(movie_id=movie_id))

        return render(request, "registration/comments.html", {
            "title": title,
            "comments": comments,
        })

def view_person_detail(request, person_id):
    # Logic to retrieve person details based on person_id
    type = request.GET.get("media_type")
    time_window = request.GET.get("time_window")
    
    person_detail = requests.get(f"https://api.themoviedb.org/3/trending/{type}/{time_window}?api_key={TMDB_API_KEY}&language=en-US")
    return JsonResponse(person_detail.json())