import os
import requests
from django.core.files.base import ContentFile
from django.utils.text import slugify
from django.conf import settings

from products.models import Game, Genre
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

    def _fetch_game_data(self, igdb_id):
        """
        Fetch full IGDB game data without creating or modifying a Game object.
        """
        query = f"""
            fields
                name,
                summary,
                genres,
                cover.image_id,
                artworks.image_id,
                screenshots.image_id,
                id;
            where id = {igdb_id};
        """

        results = self.client.query("games", query)
        if not results:
            return None

        return results[0]

    def import_game(self, igdb_id):
        """
        Import a single game by IGDB ID.
        Platform is intentionally NOT assigned here to avoid incorrect matches.
        """
        data = self._fetch_game_data(igdb_id)
        if not data:
            raise ValueError("Game not found in IGDB")

        # Title + slug
        title = data.get("name")
        base_slug = slugify(title)
        unique_slug = base_slug
        counter = 1

        # Ensure unique slug
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

        # Cover image
        if data.get("cover"):
            image_id = data["cover"]["image_id"]
            self._download_cover_image(game, image_id)

        # Banner image (artwork → screenshot fallback)
        banner_id = None
        if data.get("artworks"):
            banner_id = data["artworks"][0]["image_id"]
        elif data.get("screenshots"):
            banner_id = data["screenshots"][0]["image_id"]

        if banner_id:
            self._download_banner_image(game, banner_id)

        # Hero image (first screenshot)
        hero_id = None
        if data.get("screenshots"):
            hero_id = data["screenshots"][0]["image_id"]

        if hero_id:
            self._download_hero_image(game, hero_id)

        # Save IGDB ID
        game.igdb_id = data.get("id")
        game.save()

        return game

    def _download_banner_image(self, game, image_id):
        """
        Download a horizontal IGDB artwork/screenshot and attach it to Game.banner.
        Django handles the folder automatically.
        """
        url = f"https://images.igdb.com/igdb/image/upload/t_1080p/{image_id}.jpg"
        response = requests.get(url)

        if response.status_code != 200:
            return

        filename = f"{game.slug}-banner.jpg"
        game.banner.save(filename, ContentFile(response.content), save=True)

    def _map_genre(self, igdb_genre_id):
        """
        Map IGDB genre → Genre model using:
        1. Hardcoded fallback map
        2. Raw IGDB name
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
        Django handles the folder automatically.
        """
        url = f"{self.IMAGE_BASE}{image_id}.jpg"
        response = requests.get(url)

        if response.status_code != 200:
            return

        filename = f"{game.slug}-cover.jpg"
        game.image.save(filename, ContentFile(response.content), save=True)

    def _download_hero_image(self, game, image_id):
        """
        Download a high-resolution screenshot and save it to hero_images/.
        """
        if not image_id:
            return

        url = f"https://images.igdb.com/igdb/image/upload/t_1080p/{image_id}.jpg"
        response = requests.get(url, stream=True)

        if response.status_code == 200:
            filename = f"{game.slug}-hero.jpg"
            path = os.path.join(settings.MEDIA_ROOT, "hero_images", filename)

            # Ensure folder exists
            os.makedirs(os.path.dirname(path), exist_ok=True)

            with open(path, "wb") as out:
                for chunk in response.iter_content(1024):
                    out.write(chunk)

            game.hero_image = f"hero_images/{filename}"
            game.save()
