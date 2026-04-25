from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages

from igdb.client import IGDBClient
from igdb.importer import IGDBImporter


class IGDBAdminView(admin.ModelAdmin):
    change_list_template = "admin/igdb_search.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "search/",
                self.admin_site.admin_view(self.search_view),
                name="igdb_search"
            ),
            path(
                "import/<int:igdb_id>/",
                self.admin_site.admin_view(self.import_view),
                name="igdb_import"
            ),
        ]
        return custom_urls + urls

    def search_view(self, request):
        """
        Render search form + results.
        """
        results = None

        if "q" in request.GET:
            query = request.GET.get("q")
            client = IGDBClient()

            igdb_query = f"""
                search "{query}";
                fields
                    name,
                    cover.image_id,
                    first_release_date,
                    platforms.name,
                    id,
                    summary;
                limit 20;
            """

            results = client.query("games", igdb_query)

        return render(request, "admin/igdb_search.html", {"results": results})

    def import_view(self, request, igdb_id):
        """
        Import a game by ID.
        """
        importer = IGDBImporter()

        try:
            game = importer.import_game(igdb_id)
            messages.success(request, f"Imported: {game.title}")
        except Exception as e:
            messages.error(request, f"Import failed: {e}")

        return redirect("admin:igdb_search")
