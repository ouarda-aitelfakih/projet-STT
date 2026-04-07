"""
Modèles du module ressources pour le STT Supermarché
Développé par le binôme - L3 IDAI FST Tanger
"""

from django.db import models
from django.db import transaction
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from django.utils import timezone


class Client(models.Model):
    """
    Modèle Client - STT : Gestion de la clientèle
    Représente un client du supermarché avec suivi de son historique d'achats
    """
    nom = models.CharField(max_length=200, verbose_name="Nom complet")
    telephone = models.CharField(max_length=20, verbose_name="Téléphone")
    email = models.EmailField(blank=True, verbose_name="Email")
    adresse = models.TextField(blank=True, verbose_name="Adresse")
    date_inscription = models.DateTimeField(auto_now_add=True, verbose_name="Date d'inscription")
    client_fidele = models.BooleanField(default=False, verbose_name="Client fidèle")
    
    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"
        ordering = ['nom']
    
    def __str__(self):
        return f"{self.nom} ({self.telephone})"
    
    def clean(self):
        """STT : Validation des données du client"""
        if self.nom and len(self.nom.strip()) < 2:
            raise ValidationError("Le nom doit contenir au moins 2 caractères")
    
    @property
    def total_achats(self):
        """STT : Calcule le total des achats du client"""
        from caisse.models import Vente
        total = Vente.objects.filter(client=self, statut='validée').aggregate(
            total=models.Sum('prix_total')
        )['total'] or 0
        return total
    
    @property
    def nombre_achats(self):
        """STT : Compte le nombre d'achats du client"""
        from caisse.models import Vente
        return Vente.objects.filter(client=self, statut='validée').count()
    
    def get_historique_achats(self):
        """STT : Récupère l'historique complet des achats du client"""
        from caisse.models import Vente
        return Vente.objects.filter(client=self, statut='validée').order_by('-date_vente')


class Employe(models.Model):
    """
    Modèle Employé - STT : Gestion du personnel
    Représente un employé du supermarché avec informations de paie
    """
    POSTE_CHOICES = [
        ('caissier', 'Caissier'),
        ('gestionnaire_stock', 'Gestionnaire de stock'),
        ('manager', 'Manager'),
        ('vendeur', 'Vendeur'),
        ('agent_securite', 'Agent de sécurité'),
    ]
    
    nom = models.CharField(max_length=200, verbose_name="Nom complet")
    poste = models.CharField(max_length=50, choices=POSTE_CHOICES, verbose_name="Poste")
    taux_horaire = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Taux horaire (MAD)")
    telephone = models.CharField(max_length=20, verbose_name="Téléphone")
    email = models.EmailField(blank=True, verbose_name="Email")
    date_embauche = models.DateField(verbose_name="Date d'embauche")
    actif = models.BooleanField(default=True, verbose_name="Employé actif")
    
    class Meta:
        verbose_name = "Employé"
        verbose_name_plural = "Employés"
        ordering = ['nom']
    
    def __str__(self):
        return f"{self.nom} - {self.get_poste_display()}"
    
    def clean(self):
        """STT : Validation des données de l'employé"""
        if self.taux_horaire <= 0:
            raise ValidationError("Le taux horaire doit être positif")
        if self.date_embauche and self.date_embauche > timezone.now().date():
            raise ValidationError("La date d'embauche ne peut pas être dans le futur")
    
    @property
    def anciennete(self):
        """STT : Calcule l'ancienneté de l'employé"""
        if not self.date_embauche:
            return 0
        aujourd_hui = timezone.now().date()
        difference = aujourd_hui - self.date_embauche
        return difference.days // 365  # Années complètes
    
    def get_paies_mois(self, mois=None):
        """STT : Récupère les paies d'un mois spécifique"""
        if mois is None:
            mois = timezone.now().strftime('%Y-%m')
        return self.paie_set.filter(mois=mois)


class Paie(models.Model):
    """
    Modèle Paie - STT : Gestion de la paie
    Enregistre les bulletins de paie des employés avec calcul automatique
    """
    employe = models.ForeignKey(Employe, on_delete=models.PROTECT, verbose_name="Employé")
    heures_travaillees = models.DecimalField(max_digits=5, decimal_places=1, verbose_name="Heures travaillées")
    salaire_calcule = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True, verbose_name="Salaire calculé (MAD)")
    mois = models.CharField(max_length=20, verbose_name="Mois (AAAA-MM)")
    date_generation = models.DateTimeField(auto_now_add=True, verbose_name="Date de génération")
    statut = models.CharField(
        max_length=20,
        choices=[
            ('en_attente', 'En attente'),
            ('paye', 'Payé'),
            ('annule', 'Annulé'),
        ],
        default='en_attente',
        verbose_name="Statut"
    )
    
    class Meta:
        verbose_name = "Paie"
        verbose_name_plural = "Paies"
        ordering = ['-mois', 'employe']
        unique_together = ['employe', 'mois']  # Une paie par employé par mois
    
    def __str__(self):
        return f"Paie {self.employe.nom} - {self.mois}"
    
    def clean(self):
        """STT : Validation des données de paie"""
        if self.heures_travaillees <= 0:
            raise ValidationError("Le nombre d'heures doit être positif")
        if self.heures_travaillees > 200:  # Limite raisonnable
            raise ValidationError("Le nombre d'heures ne peut pas dépasser 200 par mois")
    
    def save(self, *args, **kwargs):
        """STT : Calcul automatique du salaire avant sauvegarde"""
        # STT : Calcul automatique du salaire
        self.salaire_calcule = self.heures_travaillees * self.employe.taux_horaire
        
        # Validation du format du mois
        if not self.mois or len(self.mois) != 7 or self.mois[4] != '-':
            self.mois = timezone.now().strftime('%Y-%m')
        
        super().save(*args, **kwargs)
    
    @classmethod
    def generer_bulletin(cls, employe_id, heures_travaillees, mois=None):
        """
        STT : Génération automatique d'un bulletin de paie
        Calcule le salaire et crée l'enregistrement de paie
        """
        try:
            employe = Employe.objects.get(id=employe_id)
            
            if mois is None:
                mois = timezone.now().strftime('%Y-%m')
            
            # Vérification si une paie existe déjà pour ce mois
            if cls.objects.filter(employe=employe, mois=mois).exists():
                raise ValidationError(f"Une paie existe déjà pour {employe.nom} au mois {mois}")
            
            paie = cls(
                employe=employe,
                heures_travaillees=heures_travaillees,
                mois=mois
            )
            paie.full_clean()
            paie.save()
            
            return paie
            
        except Employe.DoesNotExist:
            raise ValidationError("Employé non trouvé")
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Erreur lors de la génération du bulletin: {str(e)}")


class Approvisionnement(models.Model):
    """
    Modèle Approvisionnement - STT : Gestion des approvisionnements
    Enregistre les réceptions de fournisseurs avec mise à jour automatique du stock
    """
    produit = models.ForeignKey('caisse.Produit', on_delete=models.PROTECT, verbose_name="Produit")
    quantite_recue = models.IntegerField(verbose_name="Quantité reçue")
    fournisseur = models.CharField(max_length=200, verbose_name="Fournisseur")
    date_reception = models.DateTimeField(auto_now_add=True, verbose_name="Date de réception")
    cout_total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Coût total (MAD)")
    reference_facture = models.CharField(max_length=100, blank=True, verbose_name="Référence facture")
    statut = models.CharField(
        max_length=20,
        choices=[
            ('en_attente', 'En attente'),
            ('recu', 'Reçu'),
            ('annule', 'Annulé'),
        ],
        default='recu',
        verbose_name="Statut"
    )
    
    class Meta:
        verbose_name = "Approvisionnement"
        verbose_name_plural = "Approvisionnements"
        ordering = ['-date_reception']
    
    def __str__(self):
        return f"Approvisionnement {self.produit.nom} - {self.quantite_recue} unités"
    
    def clean(self):
        """STT : Validation des données d'approvisionnement"""
        if self.quantite_recue <= 0:
            raise ValidationError("La quantité reçue doit être positive")
    
    def save(self, *args, **kwargs):
        """STT : Calcul automatique du coût total avant sauvegarde"""
        # Calcul automatique du coût total basé sur le prix unitaire du produit
        if self.quantite_recue and self.produit:
            self.cout_total = self.quantite_recue * self.produit.prix_unitaire
        
        super().save(*args, **kwargs)
    
    @staticmethod
    def enregistrer_approvisionnement(produit_id, quantite_recue, fournisseur, cout_total, reference_facture=""):
        """
        STT - Propriété ACID : Atomicité
        Enregistre un approvisionnement ET incrémente le stock dans une seule transaction.
        Si l'une des deux opérations échoue, les deux sont annulées. Tout ou rien.
        """
        try:
            with transaction.atomic():
                from caisse.models import Produit
                
                # Récupération du produit avec verrouillage
                produit = Produit.objects.select_for_update().get(id=produit_id)
                
                # Création de l'approvisionnement
                approvisionnement = Approvisionnement(
                    produit=produit,
                    quantite_recue=quantite_recue,
                    fournisseur=fournisseur,
                    cout_total=cout_total,
                    reference_facture=reference_facture
                )
                approvisionnement.full_clean()
                approvisionnement.save()
                
                # Incrémentation du stock
                produit.quantite_stock += quantite_recue
                produit.save()
                
                return approvisionnement
                
        except Exception as e:
            # STT - Propriété ACID : Atomicité
            # En cas d'erreur, toute la transaction est annulée automatiquement
            raise ValidationError(f"Erreur lors de l'enregistrement de l'approvisionnement: {str(e)}")
    
    @property
    def cout_unitaire(self):
        """STT : Retourne le prix unitaire du produit"""
        return self.produit.prix_unitaire if self.produit else 0
    
    @classmethod
    def get_approvisionnements_mois(cls, mois=None):
        """STT : Récupère les approvisionnements d'un mois"""
        if mois is None:
            mois = timezone.now().strftime('%Y-%m')
        
        return cls.objects.filter(
            date_reception__year=int(mois[:4]),
            date_reception__month=int(mois[5:7]),
            statut='recu'
        )
