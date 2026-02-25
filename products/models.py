from django.db import models

class Game(models.Model):
    title = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    platform = models.CharField(max_length=50)
    genre = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='game_images/', blank=True)

    def __str__(self):
        return self.title