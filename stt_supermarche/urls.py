"""
URL configuration du projet STT Supermarché
Système de Traitement des Transactions pour supermarché marocain
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('caisse/', include('caisse.urls')),  # Module caisse - Ouarda
    path('ressources/', include('ressources.urls')),  # Module ressources - binôme
    path('', include('caisse.urls')),  # Page d'accueil vers la caisse
]
