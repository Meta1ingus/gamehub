from django.contrib import admin
from .models import Game, Platform, Genre

admin.site.register(Game)
admin.site.register(Genre)

@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    # Slugs should never be edited manually
    readonly_fields = ('slug', 'manufacturer_slug')

    list_display = ('name', 'manufacturer', 'slug', 'manufacturer_slug')
    list_filter = ('manufacturer',)
    search_fields = ('name', 'manufacturer')

    # Only superusers can add platforms
    def has_add_permission(self, request):
        return request.user.is_superuser

    # Only superusers can edit platforms
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    # Only superusers can delete platforms
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
