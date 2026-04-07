"""
Script simple pour créer des données de test
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stt_supermarche.settings')
django.setup()

from caisse.models import Produit, Vente
from ressources.models import Client, Employe, Paie, Approvisionnement
from datetime import datetime, timedelta
import random

# Créer quelques ventes manuellement
produits = list(Produit.objects.all())
clients = list(Client.objects.all())

print("Creation de ventes de test...")
for i in range(5):
    produit = random.choice(produits)
    client = random.choice(clients) if random.random() > 0.5 else None
    
    vente = Vente.objects.create(
        produit=produit,
        client=client,
        quantite=random.randint(1, 3),
        prix_unitaire=produit.prix_unitaire,
        prix_total=produit.prix_unitaire * random.randint(1, 3),
        numero_transaction=f'STT-{datetime.now().strftime("%Y%m%d%H%M%S")}-{random.randint(1000, 9999)}'
    )
    
    # Décrémenter le stock
    produit.quantite_stock -= vente.quantite
    produit.save()
    
    print(f'Vention creee: {vente.numero_transaction}')

print('Donnees de test creees avec succes!')
print(f'Total produits: {Produit.objects.count()}')
print(f'Total clients: {Client.objects.count()}')
print(f'Total ventes: {Vente.objects.count()}')
