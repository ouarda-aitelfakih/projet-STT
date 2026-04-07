"""
Configuration admin pour le module ressources du STT Supermarché
Développé par le binôme - L3 IDAI FST Tanger
"""

from django.contrib import admin
from .models import Client, Employe, Paie, Approvisionnement


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    """
    Administration des clients pour le STT
    """
    list_display = ['nom', 'telephone', 'email', 'client_fidele', 'total_achats', 'nombre_achats', 'date_inscription']
    list_filter = ['client_fidele', 'date_inscription']
    search_fields = ['nom', 'telephone', 'email']
    list_editable = ['client_fidele']
    readonly_fields = ['date_inscription', 'total_achats', 'nombre_achats']
    
    fieldsets = (
        ('Informations personnelles', {
            'fields': ('nom', 'telephone', 'email', 'adresse')
        }),
        ('Statut client', {
            'fields': ('client_fidele',)
        }),
        ('Informations système', {
            'fields': ('date_inscription', 'total_achats', 'nombre_achats'),
            'classes': ('collapse',)
        }),
    )
    
    def total_achats(self, obj):
        return f"{obj.total_achats:.2f} MAD"
    total_achats.short_description = 'Total achats'
    
    def nombre_achats(self, obj):
        return obj.nombre_achats
    nombre_achats.short_description = 'Nombre d\'achats'


@admin.register(Employe)
class EmployeAdmin(admin.ModelAdmin):
    """
    Administration des employés pour le STT
    """
    list_display = ['nom', 'poste', 'taux_horaire', 'telephone', 'actif', 'anciennete', 'date_embauche']
    list_filter = ['poste', 'actif', 'date_embauche']
    search_fields = ['nom', 'telephone', 'email']
    list_editable = ['taux_horaire', 'actif']
    readonly_fields = ['anciennete']
    
    fieldsets = (
        ('Informations personnelles', {
            'fields': ('nom', 'poste', 'telephone', 'email')
        }),
        ('Informations contractuelles', {
            'fields': ('taux_horaire', 'date_embauche', 'actif')
        }),
        ('Informations système', {
            'fields': ('anciennete',),
            'classes': ('collapse',)
        }),
    )
    
    def anciennete(self, obj):
        return f"{obj.anciennete} an(s)"
    anciennete.short_description = 'Ancienneté'


@admin.register(Paie)
class PaieAdmin(admin.ModelAdmin):
    """
    Administration des paies pour le STT
    """
    list_display = ['employe', 'mois', 'heures_travaillees', 'salaire_calcule', 'statut', 'date_generation']
    list_filter = ['statut', 'mois', 'date_generation']
    search_fields = ['employe__nom', 'mois']
    list_editable = ['statut']
    readonly_fields = ['salaire_calcule', 'date_generation']
    
    fieldsets = (
        ('Informations paie', {
            'fields': ('employe', 'mois', 'statut')
        }),
        ('Calcul salaire', {
            'fields': ('heures_travaillees', 'salaire_calcule')
        }),
        ('Informations système', {
            'fields': ('date_generation',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Approvisionnement)
class ApprovisionnementAdmin(admin.ModelAdmin):
    """
    Administration des approvisionnements pour le STT
    """
    list_display = ['produit', 'quantite_recue', 'fournisseur', 'cout_total', 'cout_unitaire', 'statut', 'date_reception']
    list_filter = ['statut', 'date_reception', 'produit__categorie']
    search_fields = ['produit__nom', 'fournisseur', 'reference_facture']
    list_editable = ['statut']
    readonly_fields = ['cout_unitaire', 'cout_total', 'date_reception']
    
    fieldsets = (
        ('Informations approvisionnement', {
            'fields': ('produit', 'fournisseur', 'reference_facture', 'statut')
        }),
        ('Détails de la réception', {
            'fields': ('quantite_recue', 'cout_total', 'cout_unitaire')
        }),
        ('Informations système', {
            'fields': ('date_reception',),
            'classes': ('collapse',)
        }),
    )
    
    def cout_unitaire(self, obj):
        return f"{obj.cout_unitaire:.2f} MAD"
    cout_unitaire.short_description = 'Coût unitaire'
