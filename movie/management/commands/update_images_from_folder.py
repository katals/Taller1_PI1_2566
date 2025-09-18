import os
import glob
from django.core.management.base import BaseCommand
from django.conf import settings
from movie.models import Movie

class Command(BaseCommand):
    help = "Assign images from media/movie/images/ to movies in DB (names like m_<TITLE>.png)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--folder",
            default=os.path.join("media", "movie", "images"),
            help="Relative or absolute path to images folder (default: media/movie/images)",
        )

    def handle(self, *args, **options):
        # 📁 Resolver carpeta de imágenes (acepta absoluta o relativa a BASE_DIR)
        folder_arg = options["folder"]
        images_folder = folder_arg
        if not os.path.isabs(images_folder):
            images_folder = os.path.join(settings.BASE_DIR, folder_arg)

        if not os.path.exists(images_folder):
            self.stderr.write(f"Images folder not found: {images_folder}")
            return

        self.stdout.write(self.style.NOTICE(f"Using images folder: {images_folder}"))

        movies = Movie.objects.all().order_by("id")
        self.stdout.write(f"Found {movies.count()} movies in DB")

        updated = 0
        missing = 0

        for movie in movies:
            title = movie.title.strip()

            # Estrategia de coincidencia de archivos:
            # 1) Intento exacto con caracteres seguros: m_<title>.png
            safe_title = "".join(c if c.isalnum() or c in " -" else "" for c in title).strip()
            candidates = [
                os.path.join(images_folder, f"m_{safe_title}.png"),
                os.path.join(images_folder, f"m_{safe_title}.jpg"),
                os.path.join(images_folder, f"m_{safe_title}.jpeg"),
            ]

            # 2) Intento flexible: reemplazar espacios por _
            if " " in safe_title:
                underscored = safe_title.replace(" ", "_")
                candidates.extend([
                    os.path.join(images_folder, f"m_{underscored}.png"),
                    os.path.join(images_folder, f"m_{underscored}.jpg"),
                    os.path.join(images_folder, f"m_{underscored}.jpeg"),
                ])

            # 3) Intento por glob insensible a mayúsculas (baja a minúsculas)
            if not any(os.path.exists(p) for p in candidates):
                pattern = os.path.join(images_folder, f"m_*")
                all_files = glob.glob(pattern)
                # match básico: igualando título sin mayúsculas/minúsculas y normalizando separadores
                normalized_title = safe_title.lower().replace(" ", "_")
                def norm(s):
                    base = os.path.basename(s)
                    return os.path.splitext(base)[0].lower()  # sin extensión
                matches = [p for p in all_files if normalized_title in norm(p)]
                candidates.extend(matches)

            # Seleccionar el primer candidato existente
            chosen = None
            for p in candidates:
                if os.path.exists(p):
                    chosen = p
                    break

            if not chosen:
                self.stderr.write(f"Image not found for movie: {title}")
                missing += 1
                continue

            # Convertir a ruta relativa para el campo ImageField (ej: movie/images/archivo.png)
            rel_root = getattr(settings, "MEDIA_ROOT", os.path.join(settings.BASE_DIR, "media"))
            # chosen debe estar dentro de MEDIA_ROOT; construimos ruta relativa a MEDIA_ROOT
            try:
                relative_path = os.path.relpath(chosen, rel_root)
            except ValueError:
                # Si no está bajo MEDIA_ROOT, intentar detectar subruta 'media/'
                if "media" in chosen:
                    relative_path = chosen.split("media" + os.sep, 1)[-1]
                else:
                    # Último recurso: usar subruta movie/images/<archivo>
                    relative_path = os.path.join("movie", "images", os.path.basename(chosen))

            movie.image = relative_path
            movie.save(update_fields=["image"])
            updated += 1
            self.stdout.write(self.style.SUCCESS(f"Updated image: {title} -> {relative_path}"))

            self.stdout.write(self.style.SUCCESS(
                f"Finished. Updated: {updated}, Missing: {missing}, Total: {movies.count()}"
            ))