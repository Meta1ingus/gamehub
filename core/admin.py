from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages

from igdb.client import IGDBClient
from igdb.importer import IGDBImporter
from .models import IGDBAdminEntry
from products.models import Platform

@admin.register(IGDBAdminEntry)
class IGDBAdmin(admin.ModelAdmin):
    change_list_template = "admin/igdb_search.html"

    # Prevent Django from querying a non‑existent table
    def get_queryset(self, request):
        return IGDBAdminEntry.objects.none()

    # Allow access to the page
    def has_view_permission(self, request, obj=None):
        return True

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("search/", self.admin_site.admin_view(self.search_view), name="igdb_search"),
            path("import/<int:igdb_id>/", self.admin_site.admin_view(self.import_view), name="igdb_import"),
        ]
        return custom_urls + urls

    def search_view(self, request):
        results = None

        if "q" in request.GET:
            query = request.GET.get("q")
            client = IGDBClient()

            igdb_query = f"""
                search "{query}";
                fields name, cover.image_id;
                limit 20;
            """

            results = client.query("games", igdb_query)
            print("IGDB RESULTS:", results)

        return render(request, "admin/igdb_search.html", {"results": results, "platforms": Platform.objects.all(),})

    def import_view(self, request, igdb_id):
        """
        Import a game by ID and assign platform.
        """
        importer = IGDBImporter()

        if request.method == "POST":
            platform_id = request.POST.get("platform")

            try:
                game = importer.import_game(igdb_id)

                if platform_id:
                    from products.models import Platform
                    platform = Platform.objects.get(id=platform_id)
                    game.platform = platform
                    game.save()

                messages.success(request, f"Imported: {game.title} (Platform: {platform.name})")

            except Exception as e:
                messages.error(request, f"Import failed: {e}")

            return redirect("admin:igdb_search")

        # If someone GETs this URL, redirect back
        return redirect("admin:igdb_search")

# Customise admin header
admin.site.site_header = "GamerBay Admin"
admin.site.site_title = "GamerBay Admin Portal"
admin.site.index_title = "Welcome to the GamerBay Administration"
