"""
Vues du module caisse pour le STT Supermarché
Développé par Ouarda - L3 IDAI FST Tanger
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.db import models
from django.db.models import Sum, Count, Avg
from datetime import datetime, timedelta
from .models import Produit, Vente
from ressources.models import Client


def accueil_caisse(request):
    """
    STT - Page d'accueil de la caisse
    Point d'entrée principal du système de traitement des transactions
    """
    # Statistiques du jour
    ventes_aujourdhui = Vente.get_ventes_du_jour()
    chiffre_affaires_jour = Vente.get_chiffre_affaires_du_jour()
    nombre_transactions = ventes_aujourdhui.count()
    
    # Produits en alerte de stock
    produits_alerte = Produit.objects.filter(quantite_stock__lte=models.F('seuil_alerte'))
    nombre_alertes = produits_alerte.count()
    
    context = {
        'nombre_transactions': nombre_transactions,
        'chiffre_affaires_jour': chiffre_affaires_jour,
        'nombre_alertes': nombre_alertes,
        'ventes_recentes': ventes_aujourdhui[:5],
    }
    return render(request, 'caisse/accueil.html', context)


def liste_produits(request):
    """
    STT - Gestion des produits
    Affiche tous les produits avec alertes de stock
    """
    produits = Produit.objects.all().order_by('nom')
    
    # STT : Filtrage par alerte de stock
    alerte_stock = request.GET.get('alerte')
    if alerte_stock == 'oui':
        produits = produits.filter(quantite_stock__lte=models.F('seuil_alerte'))
    
    # Calcul des statistiques
    produits_en_alerte = [p for p in produits if p.est_en_alerte_stock]
    produits_stock_normal = [p for p in produits if not p.est_en_alerte_stock]
    total_unites = sum(p.quantite_stock for p in produits)
    
    context = {
        'produits': produits,
        'alerte_stock': alerte_stock,
        'produits_en_alerte_count': len(produits_en_alerte),
        'produits_stock_normal_count': len(produits_stock_normal),
        'total_unites': total_unites,
    }
    return render(request, 'caisse/liste_produits.html', context)


def ajouter_produit(request):
    """
    STT - Ajout d'un nouveau produit
    Formulaire d'ajout avec validation des données
    """
    if request.method == 'POST':
        try:
            nom = request.POST.get('nom')
            prix_unitaire = request.POST.get('prix_unitaire')
            quantite_stock = request.POST.get('quantite_stock')
            seuil_alerte = request.POST.get('seuil_alerte', 10)
            categorie = request.POST.get('categorie')
            
            produit = Produit(
                nom=nom,
                prix_unitaire=prix_unitaire,
                quantite_stock=quantite_stock,
                seuil_alerte=seuil_alerte,
                categorie=categorie
            )
            produit.full_clean()
            produit.save()
            
            messages.success(request, f'Produit "{nom}" ajouté avec succès!')
            return redirect('caisse:liste_produits')
            
        except ValidationError as e:
            messages.error(request, f'Erreur de validation: {str(e)}')
        except Exception as e:
            messages.error(request, f'Erreur lors de l\'ajout du produit: {str(e)}')
    
    return render(request, 'caisse/ajouter_produit.html')


def modifier_produit(request, produit_id):
    """
    STT - Modification d'un produit existant
    Formulaire de modification avec validation
    """
    produit = get_object_or_404(Produit, id=produit_id)
    
    if request.method == 'POST':
        try:
            produit.nom = request.POST.get('nom')
            produit.prix_unitaire = request.POST.get('prix_unitaire')
            produit.quantite_stock = request.POST.get('quantite_stock')
            produit.seuil_alerte = request.POST.get('seuil_alerte')
            produit.categorie = request.POST.get('categorie')
            
            produit.full_clean()
            produit.save()
            
            messages.success(request, f'Produit "{produit.nom}" modifié avec succès!')
            return redirect('caisse:liste_produits')
            
        except ValidationError as e:
            messages.error(request, f'Erreur de validation: {str(e)}')
        except Exception as e:
            messages.error(request, f'Erreur lors de la modification: {str(e)}')
    
    context = {'produit': produit}
    return render(request, 'caisse/modifier_produit.html', context)


def nouvelle_vente(request):
    """
    STT - Propriété ACID : Atomicité
    Formulaire de vente avec transaction atomique.
    Quand une vente est validée, le stock se décrémente automatiquement 
    dans la même transaction. Si le stock est insuffisant, la transaction 
    est annulée avec un message d'erreur clair.
    """
    if request.method == 'POST':
        try:
            produit_id = request.POST.get('produit')
            quantite = int(request.POST.get('quantite'))
            client_id = request.POST.get('client') or None
            
            # STT - Propriété ACID : Atomicité
            # Utilisation de la méthode statique qui gère la transaction atomique
            vente = Vente.enregistrer_vente(produit_id, quantite, client_id)
            
            messages.success(
                request, 
                f'Venne enregistrée avec succès! Transaction: {vente.numero_transaction}'
            )
            return redirect('caisse:ticket_caisse', vente_id=vente.id)
            
        except ValidationError as e:
            messages.error(request, str(e))
        except ValueError as e:
            messages.error(request, 'La quantité doit être un nombre entier positif')
        except Exception as e:
            messages.error(request, f'Erreur lors de l\'enregistrement de la vente: {str(e)}')
    
    # Récupération des données pour le formulaire
    produits = Produit.objects.filter(quantite_stock__gt=0).order_by('nom')
    clients = Client.objects.all().order_by('nom')
    
    context = {
        'produits': produits,
        'clients': clients,
    }
    return render(request, 'caisse/nouvelle_vente.html', context)


def ticket_caisse(request, vente_id):
    """
    STT - Génération du ticket de caisse
    Affiche le ticket formaté avec toutes les informations de la transaction
    """
    vente = get_object_or_404(Vente, id=vente_id)
    
    context = {
        'vente': vente,
    }
    return render(request, 'caisse/ticket.html', context)


def historique_ventes(request):
    """
    STT - Historique des transactions
    Affiche toutes les ventes avec filtres et statistiques
    """
    # Récupération des paramètres de filtrage
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    statut = request.GET.get('statut')
    
    # STT : Filtrage des ventes
    ventes = Vente.objects.all()
    
    if date_debut:
        try:
            date_debut_obj = datetime.strptime(date_debut, '%Y-%m-%d').date()
            ventes = ventes.filter(date_vente__date__gte=date_debut_obj)
        except ValueError:
            messages.error(request, 'Format de date de début invalide')
    
    if date_fin:
        try:
            date_fin_obj = datetime.strptime(date_fin, '%Y-%m-%d').date()
            ventes = ventes.filter(date_vente__date__lte=date_fin_obj)
        except ValueError:
            messages.error(request, 'Format de date de fin invalide')
    
    if statut:
        ventes = ventes.filter(statut=statut)
    
    # Calcul des statistiques
    total_ventes = ventes.aggregate(total=models.Sum('prix_total'))['total'] or 0
    nombre_ventes = ventes.count()
    panier_moyen = total_ventes / nombre_ventes if nombre_ventes > 0 else 0
    
    context = {
        'ventes': ventes.order_by('-date_vente'),
        'total_ventes': total_ventes,
        'nombre_ventes': nombre_ventes,
        'panier_moyen': panier_moyen,
        'date_debut': date_debut,
        'date_fin': date_fin,
        'statut': statut,
    }
    return render(request, 'caisse/historique_ventes.html', context)


def statistiques_ventes(request):
    """
    STT - Tableau de bord des ventes
    Affiche les graphiques et statistiques pour le dashboard
    """
    # STT : Données pour les graphiques Chart.js
    
    # Ventes par jour sur les 7 derniers jours
    ventes_par_jour = Vente.get_ventes_par_jour(7)
    
    # Ventes par mois sur l'année en cours
    annee_courante = timezone.now().year
    ventes_par_mois = Vente.objects.filter(
        date_vente__year=annee_courante,
        statut='validée'
    ).extra({
        'mois': 'strftime("%m", date_vente)'
    }).values('mois').annotate(
        total=models.Sum('prix_total')
    ).order_by('mois')
    
    # Top 5 produits les plus vendus
    top_produits = Vente.get_top_produits(5)
    
    # Chiffre d'affaires par semaine
    date_debut_annee = datetime(annee_courante, 1, 1).date()
    ventes_annuelles = Vente.objects.filter(
        date_vente__date__gte=date_debut_annee,
        statut='validée'
    ).extra({
        'semaine': 'strftime("%W", date_vente)'
    }).values('semaine').annotate(
        total=models.Sum('prix_total')
    ).order_by('semaine')
    
    context = {
        'ventes_par_jour': list(ventes_par_jour),
        'ventes_par_mois': list(ventes_par_mois),
        'top_produits': list(top_produits),
        'ventes_annuelles': list(ventes_annuelles),
    }
    return render(request, 'caisse/statistiques.html', context)


def api_verification_stock(request, produit_id):
    """
    STT - API pour vérification en temps réel du stock
    Utilisée pour les alertes JavaScript lors de la saisie des ventes
    """
    try:
        produit = get_object_or_404(Produit, id=produit_id)
        quantite_demandee = int(request.GET.get('quantite', 1))
        
        disponibilite = {
            'disponible': produit.quantite_stock >= quantite_demandee,
            'stock_actuel': produit.quantite_stock,
            'quantite_demandee': quantite_demandee,
            'alerte_stock': produit.est_en_alerte_stock,
        }
        
        return JsonResponse(disponibilite)
        
    except (ValueError, Produit.DoesNotExist):
        return JsonResponse({'error': 'Produit invalide'}, status=400)
