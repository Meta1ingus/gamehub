from django.contrib import admin
from .models import Game, Platform, Genre, PlatformFamily

# GAME ADMIN

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    actions = ["fetch_banners_from_igdb", "find_igdb_ids"]

    list_display = (
        "title",
        "platform",
        "price",
        "is_used",
        "is_digital",
        "featured",
        "stock",
        "storefront_url",
    )

    list_display_links = ("title",)

    list_editable = (
        "price",
        "is_used",
        "is_digital",
        "featured",
        "stock",
    )

    ordering = ("title",)

    search_fields = ("title",)
    list_filter = ("platform", "is_used", "is_digital", "featured")

    # To allow storefront_url to appear in the admin form
    fields = (
        "title",
        "slug",
        "platform",
        "genre",
        "description",
        "image",
        "hero_image",
        "price",
        "is_used",
        "is_digital",
        "stock",
        "featured",
        "storefront_url",
        "igdb_id",
    )

    def fetch_banners_from_igdb(self, request, queryset):
        from igdb.importer import IGDBImporter

        importer = IGDBImporter()

        updated = 0
        skipped = 0

        for game in queryset:
            # Must have IGDB ID to fetch data
            if not hasattr(game, "igdb_id") or not game.igdb_id:
                skipped += 1
                continue

            data = importer._fetch_game_data(game.igdb_id)

            if not data:
                skipped += 1
                continue

            # Artwork → Screenshot fallback
            banner_id = None
            if data.get("artworks"):
                banner_id = data["artworks"][0]["image_id"]
            elif data.get("screenshots"):
                banner_id = data["screenshots"][0]["image_id"]

            if banner_id:
                importer._download_banner_image(game, banner_id)
                updated += 1
            else:
                skipped += 1

        self.message_user(
            request,
            f"Banners updated: {updated}. Skipped: {skipped}."
        )

    fetch_banners_from_igdb.short_description = "Fetch banners from IGDB"

    def find_igdb_ids(self, request, queryset):
        from igdb.client import IGDBClient

        client = IGDBClient()

        updated = 0
        skipped = 0

        for game in queryset:
            # Skip if already has an ID
            if game.igdb_id:
                skipped += 1
                continue

            # Search IGDB by title
            results = client.query(
                "games",
                f'search "{game.title}"; fields name, id; limit 5;'
            )

            if not results:
                skipped += 1
                continue

            # Pick the first/best match
            igdb_game = results[0]
            game.igdb_id = igdb_game["id"]
            game.save()

            updated += 1

        self.message_user(
            request,
            f"IGDB IDs updated: {updated}. Skipped: {skipped}."
        )

# GENRE ADMIN

admin.site.register(Genre)

# PLATFORM ADMIN

@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    readonly_fields = ('slug',)
    list_display = ('name', 'family', 'slug')
    list_filter = ('family',)
    search_fields = ('name', 'family__name')

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


# PLATFORM FAMILY ADMIN

@admin.register(PlatformFamily)
class PlatformFamilyAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
