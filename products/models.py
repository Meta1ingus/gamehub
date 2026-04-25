from django.db import models
from django.utils.text import slugify

class Platform(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    # Family grouping field
    family = models.ForeignKey(
        'PlatformFamily',
        on_delete=models.CASCADE,
        related_name='platforms',
        null=True,
        blank=True
    )

    image = models.ImageField(upload_to='platform_textures/', blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class PlatformFamily(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(blank=True)
    image = models.ImageField(upload_to='genre_textures/', blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Game(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True, null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    platform = models.ForeignKey(Platform, on_delete=models.SET_NULL, null=True, blank=True)
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='game_images/', blank=True)
    hero_image = models.ImageField(upload_to='hero_images/', blank=True, null=True)

    featured = models.BooleanField(default=False)
    is_used = models.BooleanField(default=False)      # False = New, True = Used
    is_digital = models.BooleanField(default=False)   # False = Physical, True = Digital

    stock = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
class GenreMapping(models.Model):
    igdb_name = models.CharField(max_length=255, unique=True)
    local_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.igdb_name} → {self.local_name}"