import os
import requests
from django.core.files.base import ContentFile
from django.utils.text import slugify

from products.models import Game, Genre, GenreMapping
from igdb.client import IGDBClient


class IGDBImporter:
    IMAGE_BASE = "https://images.igdb.com/igdb/image/upload/t_1080p/"

    # Hardcoded fallback mappings (minimal)
    GENRE_MAP = {
        "Role-playing (RPG)": "RPG",
    }

    def __init__(self):
        self.client = IGDBClient()

    def import_game(self, igdb_id):
        """
        Import a single game by IGDB ID.
        Platform is intentionally NOT assigned — you choose it manually.
        """
        query = f"""
            fields name, summary, genres, cover.image_id, screenshots.image_id;
            where id = {igdb_id};
        """

        results = self.client.query("games", query)
        if not results:
            raise ValueError("Game not found in IGDB")

        data = results[0]

        # Title + slug
        title = data.get("name")
        slug = slugify(title)

        # Create or fetch game
        game, created = Game.objects.get_or_create(
            slug=slug,
            defaults={"title": title}
        )

        # Description
        game.description = data.get("summary", "")

        # Genre mapping (first IGDB genre only)
        if data.get("genres"):
            genre_id = data["genres"][0]
            genre = self._map_genre(genre_id)
            if genre:
                game.genre = genre

        # Cover image
        if data.get("cover"):
            image_id = data["cover"]["image_id"]
            self._download_image(game, image_id, field="image")

        # Hero image (first screenshot)
        if data.get("screenshots"):
            screenshot_id = data["screenshots"][0]["image_id"]
            self._download_image(game, screenshot_id, field="hero_image")

        game.save()
        return game

    def _map_genre(self, igdb_genre_id):
        """
        Map IGDB genre → Genre model using:
        1. DB mapping (admin editable)
        2. Hardcoded fallback map
        3. Raw IGDB name
        """
        query = f"fields name; where id = {igdb_genre_id};"
        result = self.client.query("genres", query)

        if not result:
            return None

        igdb_name = result[0]["name"]

        # 1) DB mapping first
        mapping = GenreMapping.objects.filter(igdb_name=igdb_name).first()
        if mapping:
            local_name = mapping.local_name
        else:
            # 2) Hardcoded fallback
            local_name = self.GENRE_MAP.get(igdb_name, igdb_name)

        slug = slugify(local_name)

        genre, _ = Genre.objects.get_or_create(
            slug=slug,
            defaults={"name": local_name}
        )

        return genre

    def _download_image(self, game, image_id, field):
        """
        Download an IGDB image and attach it to a Game model field.
        """
        url = f"{self.IMAGE_BASE}{image_id}.jpg"
        response = requests.get(url)

        if response.status_code == 200:
            filename = f"{game.slug}-{field}.jpg"
            getattr(game, field).save(filename, ContentFile(response.content), save=False)
