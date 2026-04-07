"""
Modèles du module caisse pour le STT Supermarché
Développé par Ouarda - L3 IDAI FST Tanger
"""

from django.db import models
from django.db import transaction
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
import random


class Produit(models.Model):
    """
    Modèle Produit - STT : Gestion des stocks
    Représente un article vendable dans le supermarché avec suivi de stock
    """
    nom = models.CharField(max_length=200, verbose_name="Nom du produit")
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix unitaire (MAD)")
    quantite_stock = models.IntegerField(verbose_name="Quantité en stock")
    seuil_alerte = models.IntegerField(default=10, verbose_name="Seuil d'alerte de stock")
    categorie = models.CharField(max_length=100, verbose_name="Catégorie")
    date_ajout = models.DateTimeField(auto_now_add=True, verbose_name="Date d'ajout")
    
    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        ordering = ['nom']
    
    def __str__(self):
        return f"{self.nom} (Stock: {self.quantite_stock})"
    
    @property
    def est_en_alerte_stock(self):
        """STT : Vérifie si le produit est en alerte de stock"""
        return self.quantite_stock <= self.seuil_alerte
    
    def clean(self):
        """STT : Validation des données du produit"""
        if self.quantite_stock < 0:
            raise ValidationError("La quantité en stock ne peut pas être négative")
        if self.prix_unitaire <= 0:
            raise ValidationError("Le prix unitaire doit être positif")
        if self.seuil_alerte < 0:
            raise ValidationError("Le seuil d'alerte ne peut pas être négatif")


class Vente(models.Model):
    """
    Modèle Vente - STT : Transaction commerciale
    Enregistre chaque vente avec respect des propriétés ACID
    """
    STATUT_CHOICES = [
        ('validée', 'Validée'),
        ('annulée', 'Annulée'),
        ('en_cours', 'En cours'),
    ]
    
    produit = models.ForeignKey(Produit, on_delete=models.PROTECT, verbose_name="Produit")
    client = models.ForeignKey('ressources.Client', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Client")
    quantite = models.IntegerField(verbose_name="Quantité vendue")
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix unitaire (MAD)")
    prix_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Prix total (MAD)")
    date_vente = models.DateTimeField(auto_now_add=True, verbose_name="Date de vente")
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='validée', verbose_name="Statut")
    numero_transaction = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="Numéro de transaction")
    
    class Meta:
        verbose_name = "Vente"
        verbose_name_plural = "Ventes"
        ordering = ['-date_vente']
    
    def __str__(self):
        return f"Vente {self.numero_transaction} - {self.produit.nom} ({self.quantite}x)"
    
    def clean(self):
        """STT : Validation des données de vente"""
        if self.quantite <= 0:
            raise ValidationError("La quantité doit être positive")
        if self.prix_unitaire <= 0:
            raise ValidationError("Le prix unitaire doit être positif")
        
        # Validation du prix total s'il est déjà défini
        if self.prix_total and self.prix_total <= 0:
            raise ValidationError("Le prix total doit être positif")
    
    def save(self, *args, **kwargs):
        """STT : Sauvegarde avec génération automatique du numéro de transaction"""
        if not self.numero_transaction:
            # Génération d'un numéro de transaction unique
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            random_num = random.randint(1000, 9999)
            self.numero_transaction = f"STT-{timestamp}-{random_num}"
        
        # Calcul du prix total
        if self.quantite and self.prix_unitaire:
            self.prix_total = self.quantite * self.prix_unitaire
        
        super().save(*args, **kwargs)
    
    @staticmethod
    def enregistrer_vente(produit_id, quantite, client_id=None):
        """
        STT - Propriété ACID : Atomicité
        Enregistre une vente ET décrémente le stock dans une seule transaction.
        Si l'une des deux opérations échoue, les deux sont annulées. Tout ou rien.
        """
        try:
            with transaction.atomic():
                # Récupération du produit avec verrouillage pour éviter les conflits
                produit = Produit.objects.select_for_update().get(id=produit_id)
                
                # Vérification du stock disponible
                if produit.quantite_stock < quantite:
                    raise ValidationError(f"Stock insuffisant. Disponible: {produit.quantite_stock}, Demandé: {quantite}")
                
                # Création de la vente
                # Génération du numéro de transaction avant validation
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                random_num = random.randint(1000, 9999)
                numero_transaction = f"STT-{timestamp}-{random_num}"
                
                vente = Vente(
                    produit=produit,
                    quantite=quantite,
                    prix_unitaire=produit.prix_unitaire,
                    prix_total=quantite * produit.prix_unitaire,
                    numero_transaction=numero_transaction,
                    client_id=client_id
                )
                vente.full_clean()
                vente.save()
                
                # Décrémentation du stock
                produit.quantite_stock -= quantite
                produit.save()
                
                return vente
                
        except Exception as e:
            # STT - Propriété ACID : Atomicité
            # En cas d'erreur, toute la transaction est annulée automatiquement
            raise ValidationError(f"Erreur lors de l'enregistrement de la vente: {str(e)}")
    
    @classmethod
    def get_ventes_du_jour(cls):
        """STT : Récupère toutes les ventes du jour"""
        aujourd_hui = datetime.now().date()
        return cls.objects.filter(date_vente__date=aujourd_hui, statut='validée')
    
    @classmethod
    def get_chiffre_affaires_du_jour(cls):
        """STT : Calcule le chiffre d'affaires du jour"""
        ventes_du_jour = cls.get_ventes_du_jour()
        return ventes_du_jour.aggregate(total=models.Sum('prix_total'))['total'] or 0
    
    @classmethod
    def get_ventes_par_jour(cls, jours=7):
        """STT : Statistiques des ventes par jour pour les graphes"""
        date_fin = datetime.now().date()
        date_debut = date_fin - timedelta(days=jours-1)
        
        ventes = cls.objects.filter(
            date_vente__date__range=[date_debut, date_fin],
            statut='validée'
        ).extra({
            'jour': 'date(date_vente)'
        }).values('jour').annotate(
            total_ventes=models.Sum('prix_total'),
            nombre_ventes=models.Count('id')
        ).order_by('jour')
        
        return ventes
    
    @classmethod
    def get_top_produits(cls, limite=5):
        """STT : Top des produits les plus vendus"""
        return cls.objects.filter(statut='validée').values(
            'produit__nom'
        ).annotate(
            total_quantite=models.Sum('quantite'),
            total_vente=models.Sum('prix_total')
        ).order_by('-total_quantite')[:limite]
