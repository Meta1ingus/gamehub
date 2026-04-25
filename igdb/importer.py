import os
import requests
from django.core.files.base import ContentFile
from django.utils.text import slugify

from products.models import Game, Genre, GenreMapping
from igdb.client import IGDBClient


class IGDBImporter:
    # Use the correct IGDB cover size
    IMAGE_BASE = "https://images.igdb.com/igdb/image/upload/t_cover_big/"

    # Hardcoded fallback mappings (minimal)
    GENRE_MAP = {
        "Role-playing (RPG)": "RPG",
        "Hack and slash/Beat 'em up": "Action",
        "Real Time Strategy (RTS)": "RTS",
        "Turn-based strategy (TBS)": "Strategy",
    }

    def __init__(self):
        self.client = IGDBClient()

    def import_game(self, igdb_id):
        """
        Import a single game by IGDB ID.
        Platform is intentionally NOT assigned — you choose it manually.
        """
        query = f"""
            fields
                name,
                summary,
                genres,
                cover.image_id,
                first_release_date,
                platforms.name,
                id;
            where id = {igdb_id};
        """

        results = self.client.query("games", query)
        if not results:
            raise ValueError("Game not found in IGDB")

        data = results[0]

        # Title + slug
        title = data.get("name")
        slug = slugify(title)

        # Always create a new game with a unique slug
        base_slug = slugify(title)
        unique_slug = base_slug
        counter = 1

        while Game.objects.filter(slug=unique_slug).exists():
            unique_slug = f"{base_slug}-{counter}"
            counter += 1

        game = Game.objects.create(
            title=title,
            slug=unique_slug
        )

        # Description
        game.description = data.get("summary", "")

        # Genre mapping (first IGDB genre only)
        if data.get("genres"):
            genre_id = data["genres"][0]
            genre = self._map_genre(genre_id)
            if genre:
                game.genre = genre

        # Cover image ONLY
        if data.get("cover"):
            image_id = data["cover"]["image_id"]
            self._download_cover_image(game, image_id)

        # Extra IGDB metadata (not saved to DB yet)
        game.igdb_id = data.get("id")
        game.igdb_release_date = data.get("first_release_date")
        game.igdb_platforms = (
            [p["name"] for p in data.get("platforms", [])]
            if data.get("platforms")
            else []
        )

        game.save()
        return game

    def _map_genre(self, igdb_genre_id):
        """
        Map IGDB genre → Genre model using:
        1. Hardcoded fallback map
        2. Raw IGDB name
            If neither exists, returns None (genre not assigned).
        """
        query = f"fields name; where id = {igdb_genre_id};"
        result = self.client.query("genres", query)

        if not result:
            return None

        igdb_name = result[0]["name"]

        # Hardcoded fallback
        local_name = self.GENRE_MAP.get(igdb_name, igdb_name)

        slug = slugify(local_name)

        genre, _ = Genre.objects.get_or_create(
            slug=slug,
            defaults={"name": local_name}
        )

        return genre


    def _download_cover_image(self, game, image_id):
        """
        Download a single IGDB cover image and attach it to Game.image.
        """
        url = f"{self.IMAGE_BASE}{image_id}.jpg"
        response = requests.get(url)

        if response.status_code == 200:
            filename = f"{game.slug}-cover.jpg"
            game.image.save(filename, ContentFile(response.content), save=False)
