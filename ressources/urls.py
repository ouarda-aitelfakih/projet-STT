"""
URLs du module ressources pour le STT Supermarché
Développé par le binôme - L3 IDAI FST Tanger
"""

from django.urls import path
from . import views

app_name = 'ressources'

urlpatterns = [
    # Tableau de bord principal
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Gestion des clients
    path('clients/', views.liste_clients, name='liste_clients'),
    path('clients/ajouter/', views.ajouter_client, name='ajouter_client'),
    path('clients/fiche/<int:client_id>/', views.fiche_client, name='fiche_client'),
    
    # Gestion des employés
    path('employes/', views.liste_employes, name='liste_employes'),
    path('employes/ajouter/', views.ajouter_employe, name='ajouter_employe'),
    
    # Gestion de la paie
    path('paie/', views.gestion_paie, name='gestion_paie'),
    path('paie/generer/<int:employe_id>/', views.generer_paie, name='generer_paie'),
    
    # Gestion des approvisionnements
    path('approvisionnements/', views.approvisionnements, name='approvisionnements'),
    path('approvisionnements/enregistrer/', views.enregistrer_approvisionnement, name='enregistrer_approvisionnement'),
]
