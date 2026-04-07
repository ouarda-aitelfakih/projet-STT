"""
Configuration de l'application caisse pour le STT Supermarché
Développé par Ouarda - L3 IDAI FST Tanger
"""

from django.apps import AppConfig


class CaisseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'caisse'
    verbose_name = 'Caisse - STT Supermarché'
