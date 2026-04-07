"""
Configuration admin pour le module caisse du STT Supermarché
Développé par Ouarda - L3 IDAI FST Tanger
"""

from django.contrib import admin
from .models import Produit, Vente


@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    """
    Administration des produits pour le STT
    """
    list_display = ['nom', 'categorie', 'prix_unitaire', 'quantite_stock', 'seuil_alerte', 'est_en_alerte_stock', 'date_ajout']
    list_filter = ['categorie', 'date_ajout']
    search_fields = ['nom', 'categorie']
    list_editable = ['prix_unitaire', 'quantite_stock', 'seuil_alerte']
    readonly_fields = ['date_ajout']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('nom', 'categorie')
        }),
        ('Prix et stock', {
            'fields': ('prix_unitaire', 'quantite_stock', 'seuil_alerte')
        }),
        ('Informations système', {
            'fields': ('date_ajout',),
            'classes': ('collapse',)
        }),
    )
    
    def est_en_alerte_stock(self, obj):
        """Affiche une alerte visuelle si le stock est bas"""
        return obj.quantite_stock <= obj.seuil_alerte
    est_en_alerte_stock.boolean = True
    est_en_alerte_stock.short_description = 'Alerte stock'


@admin.register(Vente)
class VenteAdmin(admin.ModelAdmin):
    """
    Administration des ventes pour le STT
    """
    list_display = ['numero_transaction', 'produit', 'quantite', 'prix_total', 'client', 'date_vente', 'statut']
    list_filter = ['statut', 'date_vente', 'produit__categorie']
    search_fields = ['numero_transaction', 'produit__nom', 'client__nom']
    readonly_fields = ['numero_transaction', 'date_vente', 'prix_total']
    list_editable = ['statut']
    
    fieldsets = (
        ('Informations transaction', {
            'fields': ('numero_transaction', 'date_vente', 'statut')
        }),
        ('Détails de la vente', {
            'fields': ('produit', 'client', 'quantite', 'prix_unitaire', 'prix_total')
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """Le prix total est calculé automatiquement"""
        if obj:  # Modification
            return self.readonly_fields + ['prix_unitaire']
        return self.readonly_fields
