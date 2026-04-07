"""
Vues du module ressources pour le STT Supermarché
Développé par le binôme - L3 IDAI FST Tanger
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import models
from django.db.models import Sum, Count, Avg
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Client, Employe, Paie, Approvisionnement
from caisse.models import Produit, Vente


def dashboard(request):
    """
    STT - Tableau de bord principal
    Affiche les compteurs en temps réel et les graphiques Chart.js
    """
    # STT : Compteurs en temps réel
    nombre_transactions_aujourdhui = Vente.get_ventes_du_jour().count()
    chiffre_affaires_jour = Vente.get_chiffre_affaires_du_jour()
    nombre_alertes_stock = Produit.objects.filter(quantite_stock__lte=models.F('seuil_alerte')).count()
    nombre_employes_actifs = Employe.objects.filter(actif=True).count()
    
    # STT : Données pour les graphiques Chart.js
    
    # 1. Ventes par jour sur les 7 derniers jours (graphe barres)
    ventes_par_jour_data = Vente.get_ventes_par_jour(7)
    labels_jours = []
    donnees_ventes_jour = []
    
    for i in range(7):
        date = timezone.now().date() - timedelta(days=6-i)
        labels_jours.append(date.strftime('%d/%m'))
        
        # Recherche des ventes pour ce jour
        vente_jour = next((v for v in ventes_par_jour_data if v['jour'] == date.isoformat()), None)
        donnees_ventes_jour.append(float(vente_jour['total_ventes']) if vente_jour else 0)
    
    # 2. Ventes par mois sur l'année en cours (graphe ligne)
    annee_courante = timezone.now().year
    labels_mois = []
    donnees_ventes_mois = []
    mois_noms = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
    
    for mois in range(1, 13):
        ventes_mois_data = Vente.objects.filter(
            date_vente__year=annee_courante,
            date_vente__month=mois,
            statut='validée'
        ).aggregate(total=models.Sum('prix_total'))
        
        labels_mois.append(mois_noms[mois-1])
        donnees_ventes_mois.append(float(ventes_mois_data['total']) if ventes_mois_data['total'] else 0)
    
    # 3. Top 5 produits les plus vendus (graphe camembert)
    top_produits = Vente.get_top_produits(5)
    labels_produits = [p['produit__nom'] for p in top_produits]
    donnees_produits = [int(p['total_quantite']) for p in top_produits]
    
    # 4. Chiffre d'affaires cumulé par semaine (graphe aire) - TEMPORAIREMENT DÉSACTIVÉ
    labels_semaines = ['S1', 'S2', 'S3', 'S4']
    donnees_semaines = [1000, 2500, 4000, 6000]
    
    context = {
        # Compteurs
        'nombre_transactions': nombre_transactions_aujourdhui,
        'chiffre_affaires_jour': chiffre_affaires_jour,
        'nombre_alertes_stock': nombre_alertes_stock,
        'nombre_employes_actifs': nombre_employes_actifs,
        
        # Données pour Chart.js
        'labels_jours': labels_jours,
        'donnees_ventes_jour': donnees_ventes_jour,
        'labels_mois': labels_mois,
        'donnees_ventes_mois': donnees_ventes_mois,
        'labels_produits': labels_produits,
        'donnees_produits': donnees_produits,
        'labels_semaines': labels_semaines,
        'donnees_semaines': donnees_semaines,
    }
    
    return render(request, 'ressources/dashboard.html', context)


def liste_clients(request):
    """
    STT - Gestion des clients
    Affiche tous les clients avec leurs statistiques d'achat
    """
    clients = Client.objects.all().order_by('nom')
    
    # STT : Ajout des statistiques d'achat pour chaque client
    clients_data = []
    clients_fideles_count = 0
    total_achats_global = 0
    total_nombre_achats = 0
    
    for client in clients:
        client_data = {
            'client': client,
            'total_achats': client.total_achats,
            'nombre_achats': client.nombre_achats,
            'dernier_achat': client.get_historique_achats().first() if client.nombre_achats > 0 else None,
        }
        clients_data.append(client_data)
        
        if client.client_fidele:
            clients_fideles_count += 1
        total_achats_global += client.total_achats
        total_nombre_achats += client.nombre_achats
    
    context = {
        'clients_data': clients_data,
        'clients_fideles_count': clients_fideles_count,
        'total_achats_global': total_achats_global,
        'total_nombre_achats': total_nombre_achats,
    }
    return render(request, 'ressources/clients.html', context)


def fiche_client(request, client_id):
    """
    STT - Fiche détaillée d'un client
    Affiche les informations complètes et l'historique des achats
    """
    client = get_object_or_404(Client, id=client_id)
    historique_achats = client.get_historique_achats()
    
    # STT : Statistiques supplémentaires
    panier_moyen = client.total_achats / client.nombre_achats if client.nombre_achats > 0 else 0
    stats = {
        'total_achats': client.total_achats,
        'nombre_achats': client.nombre_achats,
        'panier_moyen': panier_moyen,
        'produits_achetes': historique_achats.values('produit__nom').distinct().count(),
    }
    
    context = {
        'client': client,
        'historique_achats': historique_achats,
        'stats': stats,
    }
    return render(request, 'ressources/fiche_client.html', context)


def ajouter_client(request):
    """
    STT - Ajout d'un nouveau client
    Formulaire d'ajout avec validation des données
    """
    if request.method == 'POST':
        try:
            client = Client(
                nom=request.POST.get('nom'),
                telephone=request.POST.get('telephone'),
                email=request.POST.get('email', ''),
                adresse=request.POST.get('adresse', ''),
                client_fidele=request.POST.get('client_fidele') == 'on'
            )
            client.full_clean()
            client.save()
            
            messages.success(request, f'Client "{client.nom}" ajouté avec succès!')
            return redirect('ressources:liste_clients')
            
        except ValidationError as e:
            messages.error(request, f'Erreur de validation: {str(e)}')
        except Exception as e:
            messages.error(request, f'Erreur lors de l\'ajout du client: {str(e)}')
    
    return render(request, 'ressources/ajouter_client.html')


def liste_employes(request):
    """
    STT - Gestion des employés
    Affiche tous les employés avec leurs informations
    """
    employes = Employe.objects.all().order_by('nom')
    
    # STT : Ajout des statistiques pour chaque employé
    employes_data = []
    employes_actifs_count = 0
    total_annees_experience = 0
    total_paies_global = 0
    
    for employe in employes:
        employe_data = {
            'employe': employe,
            'anciennete': employe.anciennete,
            'total_paies': employe.paie_set.aggregate(total=Sum('salaire_calcule'))['total'] or 0,
            'derniere_paie': employe.paie_set.order_by('-mois').first(),
        }
        employes_data.append(employe_data)
        
        if employe.actif:
            employes_actifs_count += 1
        total_annees_experience += employe.anciennete
        total_paies_global += employe_data['total_paies']
    
    context = {
        'employes_data': employes_data,
        'employes_actifs_count': employes_actifs_count,
        'total_annees_experience': total_annees_experience,
        'total_paies_global': total_paies_global,
    }
    return render(request, 'ressources/employes.html', context)


def ajouter_employe(request):
    """
    STT - Ajout d'un nouvel employé
    Formulaire d'ajout avec validation des données
    """
    if request.method == 'POST':
        try:
            employe = Employe(
                nom=request.POST.get('nom'),
                poste=request.POST.get('poste'),
                taux_horaire=request.POST.get('taux_horaire'),
                telephone=request.POST.get('telephone'),
                email=request.POST.get('email', ''),
                date_embauche=request.POST.get('date_embauche'),
                actif=request.POST.get('actif') == 'on'
            )
            employe.full_clean()
            employe.save()
            
            messages.success(request, f'Employé "{employe.nom}" ajouté avec succès!')
            return redirect('ressources:liste_employes')
            
        except ValidationError as e:
            messages.error(request, f'Erreur de validation: {str(e)}')
        except Exception as e:
            messages.error(request, f'Erreur lors de l\'ajout de l\'employé: {str(e)}')
    
    return render(request, 'ressources/ajouter_employe.html')


def gestion_paie(request):
    """
    STT - Gestion de la paie
    Affiche les bulletins de paie et permet d'en générer de nouveaux
    """
    # Filtres
    mois_selectionne = request.GET.get('mois', timezone.now().strftime('%Y-%m'))
    
    paies = Paie.objects.filter(mois=mois_selectionne).order_by('employe__nom')
    
    # Statistiques du mois
    stats = {
        'total_salaires': paies.aggregate(total=Sum('salaire_calcule'))['total'] or 0,
        'nombre_employes': paies.count(),
        'salaire_moyen': paies.aggregate(moyen=Avg('salaire_calcule'))['moyen'] or 0,
    }
    
    # Liste des employés sans paie pour ce mois
    employes_sans_paie = Employe.objects.filter(actif=True).exclude(
        id__in=paies.values_list('employe_id', flat=True)
    )
    
    context = {
        'paies': paies,
        'stats': stats,
        'mois_selectionne': mois_selectionne,
        'employes_sans_paie': employes_sans_paie,
    }
    return render(request, 'ressources/paie.html', context)


def generer_paie(request, employe_id):
    """
    STT - Génération automatique de la paie
    Calcule le salaire et crée le bulletin de paie
    """
    employe = get_object_or_404(Employe, id=employe_id)
    
    if request.method == 'POST':
        try:
            heures_travaillees = float(request.POST.get('heures_travaillees'))
            mois = request.POST.get('mois', timezone.now().strftime('%Y-%m'))
            
            # STT : Génération automatique du bulletin de paie
            paie = Paie.generer_bulletin(employe_id, heures_travaillees, mois)
            
            messages.success(
                request, 
                f'Bulletin de paie généré pour {employe.nom} - {paie.salaire_calcule} MAD'
            )
            return redirect('ressources:gestion_paie')
            
        except ValidationError as e:
            messages.error(request, str(e))
        except ValueError:
            messages.error(request, 'Le nombre d\'heures doit être un nombre valide')
        except Exception as e:
            messages.error(request, f'Erreur lors de la génération de la paie: {str(e)}')
    
    context = {
        'employe': employe,
        'mois_par_defaut': timezone.now().strftime('%Y-%m'),
    }
    return render(request, 'ressources/generer_paie.html', context)


def approvisionnements(request):
    """
    STT - Gestion des approvisionnements
    Affiche les réceptions de fournisseurs et permet d'en enregistrer de nouveaux
    """
    approvisionnements = Approvisionnement.objects.all().order_by('-date_reception')
    
    # Calcul des statistiques
    total_quantite_recue = sum(appro.quantite_recue for appro in approvisionnements)
    total_cout = sum(appro.cout_total for appro in approvisionnements)
    
    context = {
        'approvisionnements': approvisionnements,
        'total_quantite_recue': total_quantite_recue,
        'total_cout': total_cout,
    }
    return render(request, 'ressources/approvisionnements.html', context)


def enregistrer_approvisionnement(request):
    """
    STT - Enregistrement d'un approvisionnement
    Formulaire avec transaction atomique pour la mise à jour du stock
    """
    if request.method == 'POST':
        try:
            produit_id = request.POST.get('produit')
            quantite_recue = int(request.POST.get('quantite_recue'))
            fournisseur = request.POST.get('fournisseur')
            cout_total = float(request.POST.get('cout_total'))
            reference_facture = request.POST.get('reference_facture', '')
            
            # STT - Propriété ACID : Atomicité
            # Enregistrement avec mise à jour automatique du stock
            approvisionnement = Approvisionnement.enregistrer_approvisionnement(
                produit_id, quantite_recue, fournisseur, cout_total, reference_facture
            )
            
            messages.success(
                request,
                f'Approvisionnement enregistré! Stock de {approvisionnement.produit.nom} mis à jour.'
            )
            return redirect('ressources:approvisionnements')
            
        except ValidationError as e:
            messages.error(request, str(e))
        except ValueError:
            messages.error(request, 'Vérifiez les valeurs numériques saisies')
        except Exception as e:
            messages.error(request, f'Erreur lors de l\'enregistrement: {str(e)}')
    
    # Récupération des produits pour le formulaire
    produits = Produit.objects.all().order_by('nom')
    
    context = {
        'produits': produits,
    }
    return render(request, 'ressources/enregistrer_approvisionnement.html', context)
