import matplotlib.pyplot as plt
import matplotlib
import io
import urllib, base64

from django.shortcuts import render
from django.http import HttpResponse

from .models import Movie

import numpy as np
import os
from openai import OpenAI
from dotenv import load_dotenv

# --- Función para calcular la similitud de coseno ---
def cosine_similarity(a, b):
    """Calcula la similitud de coseno entre dos vectores a y b."""
    # Asegurarse de que los vectores no sean nulos para evitar división por cero
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return np.dot(a, b) / (norm_a * norm_b)

# --- Función para generar el embedding de un texto ---
def get_embedding(text):
    """Genera un embedding para el texto dado usando la API de OpenAI."""
    load_dotenv() # Carga las variables de entorno (tu API key)
    client = OpenAI(api_key=os.environ.get('openai_apikey'))
    
    response = client.embeddings.create(
        input=[text],
        model="text-embedding-3-small" # Mismo modelo usado para las películas
    )
    return np.array(response.data[0].embedding, dtype=np.float32)

# --- La vista principal para la página de recomendación ---
def recommend_movie(request):
    context = {} # El diccionario que pasaremos al template

    if request.method == 'POST':
        prompt = request.POST.get('prompt', '')
        
        if prompt:
            # 1. Generar el embedding del prompt del usuario
            prompt_emb = get_embedding(prompt)

            # 2. Recorrer la BD y comparar
            best_movie = None
            max_similarity = -1  # Usamos -1 porque la similitud de coseno va de -1 a 1

            for movie in Movie.objects.all():
                # Convertir el embedding binario de la película a un array de numpy
                movie_emb = np.frombuffer(movie.emb, dtype=np.float32)
                
                # Calcular la similitud
                similarity = cosine_similarity(prompt_emb, movie_emb)

                # Actualizar si encontramos una película más similar
                if similarity > max_similarity:
                    max_similarity = similarity
                    best_movie = movie
            
            # 3. Preparar el contexto para mostrar el resultado
            context['recommended_movie'] = best_movie
            context['similarity_score'] = max_similarity
            context['user_prompt'] = prompt

    return render(request, 'recommend.html', context)

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
