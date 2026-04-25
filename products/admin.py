from django.contrib import admin
from .models import Game, Platform, Genre, PlatformFamily

# GAME ADMIN

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "platform",
        "price",
        "is_used",
        "is_digital",
        "featured",
        "stock",
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
