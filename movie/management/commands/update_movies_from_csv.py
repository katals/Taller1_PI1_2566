import os
import csv
from django.core.management.base import BaseCommand
from movie.models import Movie

class Command(BaseCommand):
    help = "Update movie descriptions in the database from a CSV file"

    def handle(self, *args, **kwargs):
        # 📥 Ruta del archivo CSV con las descripciones actualizadas
        csv_file = 'updated_movie_descriptions.csv'  # ← Puedes cambiar el nombre si es necesario

        # ✅ Verifica si el archivo existe
        if not os.path.exists(csv_file):
            self.stderr.write(self.style.ERROR(f"CSV file '{csv_file}' not found. Make sure it is in the project root."))
            return

        updated_count = 0
        not_found_count = 0

        # 📖 Abrimos el CSV y leemos cada fila
        with open(csv_file, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            movies_in_csv = list(reader)
            total_movies = len(movies_in_csv)
            self.stdout.write(f"Found {total_movies} movies in CSV file.")

            for row in movies_in_csv:
                title = row['Title']
                new_description = row['Updated Description']

                try:
                    # ❗ Código completado para buscar la película por título
                    movie = Movie.objects.get(title=title)

                    # ❗ Código completado para actualizar la descripción de la película
                    movie.description = new_description
                    movie.save()
                    updated_count += 1

                    self.stdout.write(self.style.SUCCESS(f"Updated: {title}"))

                except Movie.DoesNotExist:
                    self.stderr.write(self.style.WARNING(f"Movie not found in DB: {title}"))
                    not_found_count += 1
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"Failed to update {title}: {str(e)}"))

        # ✅ Al finalizar, muestra un resumen
        self.stdout.write(self.style.SUCCESS(f"\nFinished updating. Total movies updated: {updated_count}."))
        if not_found_count > 0:
            self.stdout.write(self.style.WARNING(f"Movies not found in the database: {not_found_count}."))
