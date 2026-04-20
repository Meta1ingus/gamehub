from django.db import models

class IGDBAdminEntry(models.Model):
    class Meta:
        verbose_name = "IGDB Search"
        verbose_name_plural = "IGDB Search"
        managed = False  # No database table
