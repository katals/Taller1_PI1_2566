from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def about(request):
    #return HttpResponse("<h1>Welcome to About Page</h1>")
    return render(request, 'about.html')  # Render the home.html template


def home(request):
    #return HttpResponse("<h1>Welcome to the Movie Reviews Home Page!</h1>")
    #return render(request, 'home.html')  # Render the home.html template
    return render(request, 'home.html', {'name': 'Juan Carlos Muñoz Trejos'})  # Render the home.html template with a title context