"""
Configuration de l'application ressources pour le STT Supermarché
Développé par le binôme - L3 IDAI FST Tanger
"""

from django.apps import AppConfig


class RessourcesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ressources'
    verbose_name = 'Ressources - STT Supermarché'
