"""
Script de peuplement de la base de données pour le STT Supermarché
Génère des données réalistes pour tester le système
"""

import os
import sys
import django
from datetime import datetime, timedelta
import random

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stt_supermarche.settings')
django.setup()

from caisse.models import Produit, Vente
from ressources.models import Client, Employe, Paie, Approvisionnement


def creer_produits():
    """Crée les produits typiques d'un supermarché marocain"""
    print("Creation des produits...")
    
    produits_data = [
        {"nom": "Huile de tournesol 1L", "prix": 35.50, "stock": 45, "seuil": 10, "categorie": "Alimentaire"},
        {"nom": "Sucre semoule 1kg", "prix": 12.00, "stock": 120, "seuil": 20, "categorie": "Epicerie"},
        {"nom": "Farine blanche 1kg", "prix": 8.50, "stock": 80, "seuil": 15, "categorie": "Epicerie"},
        {"nom": "Lait Centrale 1L", "prix": 7.50, "stock": 25, "seuil": 8, "categorie": "Produits laitiers"},
        {"nom": "Beurre 250g", "prix": 22.00, "stock": 35, "seuil": 10, "categorie": "Produits laitiers"},
        {"nom": "Café Moulu 200g", "prix": 45.00, "stock": 18, "seuil": 5, "categorie": "Epicerie"},
        {"nom": "Thé vert 100g", "prix": 28.00, "stock": 42, "seuil": 12, "categorie": "Epicerie"},
        {"nom": "Pain de mie", "prix": 15.00, "stock": 20, "seuil": 6, "categorie": "Boulangerie"},
        {"nom": "Eau minérale 1.5L", "prix": 6.00, "stock": 150, "seuil": 30, "categorie": "Boissons"},
        {"nom": "Jus d'orange 1L", "prix": 18.50, "stock": 38, "seuil": 10, "categorie": "Boissons"},
    ]
    
    for prod_data in produits_data:
        produit, created = Produit.objects.get_or_create(
            nom=prod_data["nom"],
            defaults={
                "prix_unitaire": prod_data["prix"],
                "quantite_stock": prod_data["stock"],
                "seuil_alerte": prod_data["seuil"],
                "categorie": prod_data["categorie"],
            }
        )
        if created:
            print(f"  [OK] Produit cree: {produit.nom}")
        else:
            print(f"  [ATT] Produit existe deja: {produit.nom}")


def creer_clients():
    """Crée des clients marocains typiques"""
    print("\nCreation des clients...")
    
    clients_data = [
        {"nom": "Mohammed Alami", "telephone": "0612345678", "email": "m.alami@email.com", "fidele": True},
        {"nom": "Fatima Zahra", "telephone": "0623456789", "email": "f.zahra@email.com", "fidele": False},
        {"nom": "Abdelkader Bennani", "telephone": "0634567890", "email": "", "fidele": True},
        {"nom": "Aicha El Idrissi", "telephone": "0645678901", "email": "a.idrissi@email.com", "fidele": False},
        {"nom": "Youssef Amrani", "telephone": "0656789012", "email": "y.amrani@email.com", "fidele": True},
    ]
    
    for client_data in clients_data:
        client, created = Client.objects.get_or_create(
            nom=client_data["nom"],
            defaults={
                "telephone": client_data["telephone"],
                "email": client_data["email"],
                "client_fidele": client_data["fidele"],
            }
        )
        if created:
            print(f"  [OK] Client cree: {client.nom}")
        else:
            print(f"  [ATT] Client existe deja: {client.nom}")


def creer_employes():
    """Crée des employés pour le supermarché"""
    print("\nCreation des employes...")
    
    employes_data = [
        {"nom": "Karim Reda", "poste": "caissier", "taux": 25.00, "telephone": "0661234567"},
        {"nom": "Samira Benjelloun", "poste": "gestionnaire_stock", "taux": 30.00, "telephone": "0672345678"},
        {"nom": "Rachid El Mokhtar", "poste": "manager", "taux": 45.00, "telephone": "0683456789"},
    ]
    
    for emp_data in employes_data:
        employe, created = Employe.objects.get_or_create(
            nom=emp_data["nom"],
            defaults={
                "poste": emp_data["poste"],
                "taux_horaire": emp_data["taux"],
                "telephone": emp_data["telephone"],
                "date_embauche": datetime.now().date() - timedelta(days=random.randint(30, 365)),
            }
        )
        if created:
            print(f"  [OK] Employe cree: {employe.nom}")
        else:
            print(f"  [ATT] Employe existe deja: {employe.nom}")


def creer_ventes():
    """Crée des ventes sur les 30 derniers jours"""
    print("\nCreation des ventes...")
    
    produits = list(Produit.objects.all())
    clients = list(Client.objects.all())
    
    if not produits:
        print("  [ERREUR] Aucun produit trouve. Creez d'abord les produits.")
        return
    
    ventes_creees = 0
    for i in range(20):  # 20 ventes aléatoires
        # Date aléatoire dans les 30 derniers jours
        jours_aleatoires = random.randint(0, 29)
        date_vente = datetime.now() - timedelta(days=jours_aleatoires)
        
        # Produit et quantité aléatoires
        produit = random.choice(produits)
        quantite = random.randint(1, min(5, produit.quantite_stock))
        
        # Client aléatoire (ou anonyme)
        client = random.choice(clients) if random.random() > 0.3 else None
        
        try:
            vente = Vente.enregistrer_vente(
                produit_id=produit.id,
                quantite=quantite,
                client_id=client.id if client else None
            )
            
            # Modifier la date pour simuler des ventes passées
            vente.date_vente = date_vente
            vente.save()
            
            ventes_creees += 1
            print(f"  [OK] Vente creee: {vente.numero_transaction} ({vente.produit.nom} x{vente.quantite})")
            
        except Exception as e:
            print(f"  [ERREUR] Erreur lors de la creation de la vente: {str(e)}")
    
    print(f"\n  [STAT] Total ventes creees: {ventes_creees}")


def creer_approvisionnements():
    """Crée des approvisionnements pour tester la gestion des stocks"""
    print("\nCreation des approvisionnements...")
    
    produits = list(Produit.objects.all())
    
    if not produits:
        print("  [ERREUR] Aucun produit trouve.")
        return
    
    fournisseurs = ["Fournisseur Alimentaire SA", "Boissons du Maroc", "Epicerie Centrale", "Laiterie Nord"]
    
    for i in range(8):  # 8 approvisionnements
        produit = random.choice(produits)
        quantite = random.randint(20, 100)
        cout_unitaire = produit.prix_unitaire * random.uniform(0.7, 0.85)  # Prix d'achat
        cout_total = quantite * cout_unitaire
        fournisseur = random.choice(fournisseurs)
        
        try:
            approvisionnement = Approvisionnement.enregistrer_approvisionnement(
                produit_id=produit.id,
                quantite_recue=quantite,
                fournisseur=fournisseur,
                cout_total=cout_total,
                reference_facture=f"F{random.randint(1000, 9999)}"
            )
            print(f"  [OK] Approvisionnement cree: {approvisionnement.produit.nom} (+{quantite})")
            
        except Exception as e:
            print(f"  [ERREUR] Erreur lors de la creation de l'approvisionnement: {str(e)}")


def creer_paies():
    """Crée des bulletins de paie pour le mois en cours"""
    print("\nCreation des paies...")
    
    employes = list(Employe.objects.filter(actif=True))
    mois_courant = datetime.now().strftime('%Y-%m')
    
    if not employes:
        print("  [ERREUR] Aucun employe actif trouve.")
        return
    
    for employe in employes:
        heures = random.uniform(120, 180)  # Heures mensuelles réalistes
        
        try:
            paie = Paie.generer_bulletin(
                employe_id=employe.id,
                heures_travaillees=heures,
                mois=mois_courant
            )
            print(f"  [OK] Paie creee: {employe.nom} - {paie.salaire_calcule:.2f} MAD")
            
        except Exception as e:
            print(f"  [ATT] Paie existe deja ou erreur: {employe.nom} - {str(e)}")


def main():
    """Fonction principale de peuplement"""
    print("Demarrage du peuplement de la base de donnees STT Supermarche")
    print("=" * 60)
    
    try:
        creer_produits()
        creer_clients()
        creer_employes()
        creer_ventes()
        creer_approvisionnements()
        creer_paies()
        
        print("\n" + "=" * 60)
        print("Peuplement termine avec succes!")
        print("\nResume des donnees creees:")
        print(f"   Produits: {Produit.objects.count()}")
        print(f"   Clients: {Client.objects.count()}")
        print(f"   Employes: {Employe.objects.count()}")
        print(f"   Ventes: {Vente.objects.count()}")
        print(f"   Approvisionnements: {Approvisionnement.objects.count()}")
        print(f"   Paies: {Paie.objects.count()}")
        
        print("\nLe systeme est pret pour les tests!")
        print("   Lancez: python manage.py runserver")
        print("   Acces: http://127.0.0.1:8000")
        
    except Exception as e:
        print(f"\nErreur lors du peuplement: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
