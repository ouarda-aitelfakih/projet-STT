"""
URLs du module caisse pour le STT Supermarché
Développé par Ouarda - L3 IDAI FST Tanger
"""

from django.urls import path
from . import views

app_name = 'caisse'

urlpatterns = [
    # Page d'accueil de la caisse
    path('', views.accueil_caisse, name='accueil'),
    
    # Gestion des produits
    path('produits/', views.liste_produits, name='liste_produits'),
    path('produits/ajouter/', views.ajouter_produit, name='ajouter_produit'),
    path('produits/modifier/<int:produit_id>/', views.modifier_produit, name='modifier_produit'),
    
    # Gestion des ventes - STT : Transactions
    path('vente/nouvelle/', views.nouvelle_vente, name='nouvelle_vente'),
    path('vente/ticket/<int:vente_id>/', views.ticket_caisse, name='ticket_caisse'),
    path('ventes/historique/', views.historique_ventes, name='historique_ventes'),
    path('ventes/statistiques/', views.statistiques_ventes, name='statistiques_ventes'),
    
    # API pour vérification en temps réel
    path('api/verification-stock/<int:produit_id>/', views.api_verification_stock, name='verification_stock'),
]
