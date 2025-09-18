import numpy as np
from django.core.management.base import BaseCommand
from movie.models import Movie

class Command(BaseCommand):
    """
    Comando de Django para seleccionar una película al azar y mostrar sus embeddings.
    """
    help = 'Muestra los embeddings de una película seleccionada al azar de la base de datos.'

    def handle(self, *args, **kwargs):
        # Usamos order_by('?') para obtener un objeto aleatorio de la base de datos.
        # .first() asegura que solo obtenemos uno.
        random_movie = Movie.objects.order_by('?').first()

        if not random_movie:
            self.stdout.write(self.style.ERROR('❌ No se encontraron películas en la base de datos.'))
            return

        self.stdout.write(self.style.SUCCESS(f"🎬 Película seleccionada al azar: '{random_movie.title}'"))

        try:
            # Recuperamos el embedding desde el campo binario
            # Es crucial usar el mismo dtype (np.float32) con el que se guardó
            embedding_vector = np.frombuffer(random_movie.emb, dtype=np.float32)

            self.stdout.write("--------------------------------------------------")
            self.stdout.write("🔍 Vector de embedding recuperado:")
            self.stdout.write(f"   Dimensiones (shape): {embedding_vector.shape}")
            self.stdout.write(f"   Primeros 5 valores: {embedding_vector[:5]}")
            self.stdout.write("--------------------------------------------------")
            self.stdout.write(self.style.SUCCESS('✅ ¡Comando ejecutado exitosamente!'))

        except Exception as e:
            self.stderr.write(f"❌ Error al procesar el embedding para '{random_movie.title}': {e}")