import matplotlib.pyplot as plt
import matplotlib
import io
import urllib, base64

from django.shortcuts import render
from django.http import HttpResponse

from .models import Movie

# Create your views here.

def about(request):
    #return HttpResponse("<h1>Welcome to About Page</h1>")
    return render(request, 'about.html')  # Render the home.html template


def home(request):
    #return HttpResponse("<h1>Welcome to the Movie Reviews Home Page!</h1>")
    #return render(request, 'home.html')  # Render the home.html template
    searchTerm = request.GET.get('searchMovie')
    if searchTerm:
        movies = Movie.objects.filter(title__icontains=searchTerm)  # Filter movies based on search term
    else:
        movies = Movie.objects.all()
    return render(request, 'home.html', {'searchTerm': searchTerm, 'movies': movies})  # Render the home.html template with a title context and movie list

def statistics_view(request):
    matplotlib.use('Agg')
    all_movies = Movie.objects.all()

    # ---------------- Gráfica por año ----------------
    movie_counts_by_year = {}
    for movie in all_movies:
        year = movie.year if movie.year else "None"
        movie_counts_by_year[year] = movie_counts_by_year.get(year, 0) + 1

    plt.bar(range(len(movie_counts_by_year)), movie_counts_by_year.values())
    plt.title('Movies per year')
    plt.xlabel('Year')
    plt.ylabel('Number of movies')
    plt.xticks(range(len(movie_counts_by_year)), movie_counts_by_year.keys(), rotation=90)
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=150)
    buffer.seek(0)
    plt.close()
    graphic_year = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()

    # ---------------- Gráfica por género (primer género) ----------------
    from collections import Counter
    import re
    counts = Counter()
    for m in all_movies:
        raw = (m.genre or "").strip()
        if not raw:   # si el campo está vacío o NULL, la ignora
            continue
        first_genre = re.split(r'[,/|;]', raw)[0].strip()
        counts[first_genre] += 1


    genres = list(counts.keys())   # tal cual están, sin ordenar
    values = list(counts.values())

    
    plt.bar(range(len(genres)), values, color="green")
    plt.title('Movies per genre (first only)')
    plt.xlabel('Genre')
    plt.ylabel('Number of movies')
    
    # Mejorar la visualización de las etiquetas
    plt.xticks(range(len(genres)), genres, rotation=45, ha='right')
    
    # Ajustar automáticamente el layout para evitar cortes
    plt.tight_layout()
    
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
    buffer.seek(0)
    plt.close()
    graphic_genre = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()

    # Enviar ambas al template
    return render(request, 'statistics.html', {
        'graphic_year': graphic_year,
        'graphic_genre': graphic_genre,})

def signup(request):
    email = request.GET.get('email')
    return render(request, 'signup.html', {'email': email})  # Render the signup.html template with the email context   
