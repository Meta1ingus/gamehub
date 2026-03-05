from django.core.management.base import BaseCommand
from products.models import Platform, Genre, Game
from django.utils.text import slugify
import random

class Command(BaseCommand):
    help = "Seeds the database with dummy platforms, genres, and games."

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Seeding dummy data..."))

        # --- Platforms ---
        platform_names = ["PlayStation 5", "Xbox Series X", "Nintendo Switch", "PC"]
        platforms = []

        for name in platform_names:
            platform, created = Platform.objects.get_or_create(
                name=name,
                defaults={"slug": slugify(name)}
            )
            platforms.append(platform)

        # --- Genres ---
        genre_names = ["Action", "Adventure", "RPG", "Shooter", "Puzzle", "Sports"]
        genres = []

        for name in genre_names:
            genre, created = Genre.objects.get_or_create(
                name=name,
                defaults={"slug": slugify(name)}
            )
            genres.append(genre)

        # --- Games ---
        for i in range(20):
            title = f"Game {i+1}"
            Game.objects.get_or_create(
                title=title,
                defaults={
                    "slug": slugify(title),
                    "price": random.randint(10, 60),
                    "platform": random.choice(platforms),
                    "genre": random.choice(genres),
                }
            )

        self.stdout.write(self.style.SUCCESS("Dummy data seeded successfully!"))