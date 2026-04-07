# STT Supermarché - Système de Traitement des Transactions

Projet développé dans le cadre du cours L3 IDAI - FST Tanger

## 📋 Description

STT Supermarché est une application web de gestion complète pour supermarché développée avec Django. Le système permet de gérer les ventes, les stocks, les clients, les employés et les approvisionnements tout en respectant les propriétés ACID des transactions.


## Lien de Védio


## 🚀 Fonctionnalités

### 🛒 Module Caisse
- **Gestion des ventes** : Enregistrement des transactions avec calcul automatique
- **Gestion des produits** : Suivi des stocks avec alertes de seuil
- **Historique des ventes** : Traçabilité complète des transactions
- **Statistiques** : Chiffre d'affaires, top produits, ventes par période

### 👥 Module Ressources
- **Gestion des clients** : Fiches clients avec historique d'achats
- **Gestion des employés** : Suivi du personnel avec calcul d'ancienneté
- **Gestion de la paie** : Bulletins de paie automatiques avec calcul salarial
- **Approvisionnements** : Réceptions fournisseurs avec mise à jour automatique du stock

### 📊 Tableau de bord
- **Compteurs en temps réel** : Transactions du jour, chiffre d'affaires
- **Graphiques Chart.js** : Visualisations des ventes par jour/mois
- **Alertes de stock** : Notifications automatiques

## 🏗️ Architecture

### Propriétés ACID
- **Atomicité** : Les transactions (ventes, approvisionnements) sont atomiques
- **Cohérence** : Calculs automatiques et validations intégrées
- **Isolation** : Verrouillage des enregistrements lors des modifications
- **Durabilité** : Sauvegarde fiable des données

### Structure des modèles
```
caisse/
├── Produit (gestion des stocks)
├── Vente (transactions commerciales)

ressources/
├── Client (gestion de la clientèle)
├── Employe (gestion du personnel)
├── Paie (bulletins de paie)
└── Approvisionnement (réceptions fournisseurs)
```

## 🛠️ Installation

### Prérequis
- Python 3.8+
- Django 6.0+
- SQLite (base de données par défaut)

### Configuration
```bash
# Cloner le projet
git clone <repository-url>
cd projet-STT

# Installer les dépendances
pip install -r requirements.txt

# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Lancer le serveur
python manage.py runserver
```

## 📝 Utilisation

### Accès au système
- **Interface principale** : http://127.0.0.1:8000/
- **Administration** : http://127.0.0.1:8000/admin/

### Flux de travail typique
1. **Approvisionnement** : Réception des produits des fournisseurs
2. **Vente** : Enregistrement des ventes clients
3. **Gestion** : Suivi des stocks, paies, clients
4. **Rapports** : Analyse des performances via le dashboard

## 🔧 Caractéristiques techniques

### Calculs automatiques
- **Prix total vente** : `quantité × prix_unitaire`
- **Salaire employé** : `heures_travaillées × taux_horaire`
- **Coût total approvisionnement** : `quantité_recue × prix_unitaire_produit`
- **Coût unitaire approvisionnement** : Récupéré depuis le prix du produit

### Validations intégrées
- **Stock suffisant** avant vente
- **Valeurs positives** pour tous les montants
- **Dates valides** (pas dans le futur)
- **Uniques** : numéros de transaction, paies par employé/mois

### Interface utilisateur
- **Bootstrap 5** pour un design moderne et responsive
- **Chart.js** pour les visualisations de données
- **Messages Django** pour les notifications utilisateur
- **Admin Django** pour la gestion back-office

## 📊 Données de test

Le projet inclut des scripts de génération de données de test :
- `seed_data.py` : Données complètes pour démonstration
- `create_test_data.py` : Génération aléatoire de données

## 🎯 Points forts du projet

### ✅ Qualités techniques
- **Propriétés ACID** respectées dans toutes les transactions
- **Calculs automatiques** fiables et cohérents
- **Interface intuitive** avec feedback utilisateur
- **Code organisé** et maintenable

### 📈 Fonctionnalités métier
- **Gestion complète** d'un supermarché
- **Traçabilité** des transactions
- **Alertes automatiques** de gestion de stock
- **Rapports** et statistiques détaillés

## 🤝 Développement

### Équipe
- **Ouarda Ait Elfakih** & **Halima Achabbak**  

 

### Technologies utilisées
- **Backend** : Django 6.0, Python 3.14
- **Frontend** : HTML5, CSS3, Bootstrap 5, JavaScript
- **Base de données** : SQLite
- **Graphiques** : Chart.js
- **Déploiement** : Serveur de développement Django

## 📝 Notes de développement

### Corrections récentes
- **Gestion des valeurs None** dans les propriétés et validations
- **Calculs automatiques** des coûts et prix
- **Validation robuste** des formulaires admin
- **Gestion des erreurs** avec messages utilisateur clairs

### Améliorations possibles
- **Export PDF** des bulletins de paie
- **Notifications email** pour alertes de stock
- **API REST** pour intégrations externes
- **Dashboard avancé** avec plus de métriques


---

*Projet académique démontrant la maîtrise du framework Django et des principes de gestion de bases de données relationnelles.*
