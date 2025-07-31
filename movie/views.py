from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def about(request):
    return HttpResponse("<h1>Welcome to About Page</h1>")

def home(request):
    #return HttpResponse("<h1>Welcome to the Movie Reviews Home Page!</h1>")
    return render(request, 'home.html')  # Render the home.html template