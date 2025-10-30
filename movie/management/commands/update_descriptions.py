import os
from openai import OpenAI
from django.core.management.base import BaseCommand
from movie.models import Movie
from dotenv import load_dotenv

class Command(BaseCommand):
    help = "Update movie descriptions using OpenAI API"

    def handle(self, *args, **kwargs):
        # ✅ Load environment variables from the .env file in the project root
        load_dotenv()
        # ✅ Get the API key from environment variables (prefer standard OPENAI_API_KEY, fallback to legacy openai_apikey)
        api_key = (os.getenv('OPENAI_API_KEY') or os.getenv('openai_apikey') or '').strip()
        # ✅ Validate API key presence
        if not api_key:
            self.stderr.write(self.style.ERROR(
                "OpenAI API key not found. Set OPENAI_API_KEY (or openai_apikey) in your .env next to manage.py, without quotes."
            ))
            return
        # ✅ Initialize the OpenAI client with the API key
        client = OpenAI(api_key=api_key)
        # ✅ Helper function to send prompt and get completion from OpenAI
        def get_completion(prompt, model="gpt-3.5-turbo"):
            messages = [{"role": "user", "content": prompt}]
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0,  # For deterministic, consistent responses
            )
            return response.choices[0].message.content.strip()

        # ✅ Instruction to guide the AI response
        instruction = (
            "Vas a actuar como un aficionado del cine que sabe describir de forma clara, "
            "concisa y precisa cualquier película en menos de 200 palabras. La descripción "
            "debe incluir el género de la película y cualquier información adicional que sirva "
            "para crear un sistema de recomendación."
        )

        # ✅ Fetch all movies from the database
        movies = Movie.objects.all()
        if not movies.exists():
            self.stdout.write(self.style.WARNING("No movies found in the database."))
            return
            
        self.stdout.write(f"Found {movies.count()} movies to process.")

        # ✅ Process each movie
        for movie in movies:
            self.stdout.write(f"Processing: {movie.title}")
            try:
                # ✅ Construct the prompt
                prompt = (
                    f"{instruction} "
                    f"Vas a actualizar la descripción '{movie.description}' de la película '{movie.title}'."
                )

                # ✅ Get the new description from the AI
                updated_description = get_completion(prompt)

                # ✅ Save the new description to the database
                movie.description = updated_description
                movie.save()

                self.stdout.write(self.style.SUCCESS(f"Successfully updated: {movie.title}"))

            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Failed to update {movie.title}: {str(e)}"))
            
            # ✅ The break statement will stop the command after processing one movie.
            self.stdout.write(self.style.WARNING("Stopping after one movie due to 'break' statement."))
            break
        
        self.stdout.write(self.style.SUCCESS("\nFinished processing."))

