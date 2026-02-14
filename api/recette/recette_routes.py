from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select, and_, func
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel

from api.recette.recette_model import RapportMensuel, RecetteCreate, RecetteResponse, RecetteUpdate
from api.recette.recette_services import get_solde_anterieur, recalculer_soldes_apres_date
from models.eglise_models import Recette, Type

from core.database import get_session

router = APIRouter()



@router.get("/{idRecette}", response_model=RecetteResponse)
def get_recette(idRecette: int, db: Session = Depends(get_session)):
    """Récupérer une recette par son ID"""
    recette = db.get(Recette, idRecette)
    if not recette:
        raise HTTPException(status_code=404, detail="Recette non trouvée")
    return recette

@router.get("/", response_model=List[RecetteResponse])
def get_all_recettes(
    skip: int = 0,
    limit: int = 100,
    date_debut: Optional[date] = None,
    date_fin: Optional[date] = None,
    db: Session = Depends(get_session)
):
    """Récupérer toutes les recettes avec filtres optionnels"""
    stmt = select(Recette).order_by(Recette.date, Recette.idRecette)
    
    if date_debut:
        stmt = stmt.where(Recette.date >= date_debut)
    if date_fin:
        stmt = stmt.where(Recette.date <= date_fin)
    
    stmt = stmt.offset(skip).limit(limit)
    recettes = db.exec(stmt).all()
    return recettes
@router.post("/create", response_model=RecetteResponse)
def create_recette(recette_data: RecetteCreate, db: Session = Depends(get_session)):
    """Créer une nouvelle recette avec calcul automatique du solde"""
    
    # Récupérer le solde antérieur à cette date
    solde_anterieur = get_solde_anterieur(db, recette_data.date,recette_data.type_id)
    
    # Calculer le nouveau solde
    nouveau_solde = solde_anterieur - recette_data.debit_montant + recette_data.credit_montant
    
    # Créer la nouvelle recette
    nouvelle_recette = Recette(
        date=recette_data.date,
        libelle=recette_data.libelle,
        debit_montant=recette_data.debit_montant,
        credit_montant=recette_data.credit_montant,
        type_id=recette_data.type_id,
        solde=nouveau_solde
    )
    
    db.add(nouvelle_recette)
    db.commit()
    db.refresh(nouvelle_recette)
    
    # Recalculer tous les soldes après cette date
    recalculer_soldes_apres_date(db, recette_data.date,recette_data.type_id)
    
    return nouvelle_recette
# ============= CRUD UPDATE =============
@router.put("/{idRecette}", response_model=RecetteResponse)
def update_recette(
    idRecette: int,
    recette_data: RecetteUpdate,
    db: Session = Depends(get_session)
):
    """Mettre à jour une recette et recalculer les soldes"""
    recette = db.get(Recette, idRecette)
    if not recette:
        raise HTTPException(status_code=404, detail="Recette non trouvée")
    
    ancienne_date = recette.date
    
    # Mettre à jour les champs
    if recette_data.date is not None:
        recette.date = recette_data.date
    if recette_data.libelle is not None:
        recette.libelle = recette_data.libelle
    if recette_data.debit_montant is not None:
        recette.debit_montant = recette_data.debit_montant
    if recette_data.credit_montant is not None:
        recette.credit_montant = recette_data.credit_montant
    if recette_data.solde is not None:
        recette.solde = recette_data.solde
    
    db.add(recette)
    db.commit()
    
    # Recalculer les soldes à partir de la date la plus ancienne
    date_recalcul = min(ancienne_date, recette.date)
    recalculer_soldes_apres_date(db, date_recalcul,recette_data.type_id)
    
    db.refresh(recette)
    return recette


@router.get("/", response_model=List[RecetteResponse])
def get_all_recettes(
    skip: int = 0,
    limit: int = 100,
    date_debut: Optional[date] = None,
    date_fin: Optional[date] = None,
    afficher_solde: bool = True,
    db: Session = Depends(get_session)
):
    """Récupérer toutes les recettes avec filtres optionnels"""
    stmt = select(Recette).order_by(Recette.date, Recette.idRecette)
    
    # Filtre pour exclure les lignes avec libelle="solde" si demandé
    if not afficher_solde:
        stmt = stmt.where(
            (Recette.libelle == None) | 
            (Recette.libelle.ilike("%solde%") == False)
        )
    
    if date_debut:
        stmt = stmt.where(Recette.date >= date_debut)
    if date_fin:
        stmt = stmt.where(Recette.date <= date_fin)
    
    stmt = stmt.offset(skip).limit(limit)
    recettes = db.exec(stmt).all()
    return recettes




# ============= CRUD DELETE =============
@router.delete("/{idRecette}")
def delete_recette(idRecette: int, db: Session = Depends(get_session)):
    """Supprimer une recette et recalculer les soldes"""
    recette = db.get(Recette, idRecette)
    if not recette:
        raise HTTPException(status_code=404, detail="Recette non trouvée")
    
    date_suppression = recette.date
    db.delete(recette)
    db.commit()
    
    return {"message": "Recette supprimée avec succès"}

# ============= RAPPORTS PAR TYPE ET MOIS =============
@router.get("/rapport/mensuel/{annee}/{mois}", response_model=List[RapportMensuel])
def get_rapport_mensuel_par_type(
    annee: int,
    mois: int,
    afficher_solde: bool = False,
    db: Session = Depends(get_session)
):
    """
    Génère un rapport mensuel groupé par type
    Exemple: /rapport/mensuel/2025/1 pour janvier 2025
    Par défaut, n'affiche pas les lignes avec libelle="solde"
    """
    from calendar import monthrange
    
    # Définir les dates de début et fin du mois
    premier_jour = date(annee, mois, 1)
    dernier_jour = date(annee, mois, monthrange(annee, mois)[1])
    
    # Récupérer toutes les recettes du mois
    stmt = (
        select(Recette)
        .where(
            and_(
                Recette.date >= premier_jour,
                Recette.date <= dernier_jour
            )
        )
        .order_by(Recette.date, Recette.idRecette)
    )
    
    # Exclure les lignes avec libelle="solde" si demandé
    if not afficher_solde:
        stmt = stmt.where(
            (Recette.libelle == None) | 
            (Recette.libelle.ilike("%solde%") == False)
        )
    
    recettes = db.exec(stmt).all()
    
    # Grouper par type
    rapports_par_type = {}
    
    for recette in recettes:
        type_nom = recette.type.nom if recette.type else "Sans type"
        
        if type_nom not in rapports_par_type:
            rapports_par_type[type_nom] = {
                "operations": [],
                "total_debits": 0,
                "total_credits": 0
            }
        
        rapports_par_type[type_nom]["operations"].append(recette)
        rapports_par_type[type_nom]["total_debits"] += recette.debit_montant
        rapports_par_type[type_nom]["total_credits"] += recette.credit_montant
    
    # Créer les rapports
    mois_noms = [
        "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
        "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"
    ]
    
    rapports = []
    for type_nom, data in rapports_par_type.items():
        solde_final = data["operations"][-1].solde if data["operations"] else 0
        
        rapport = RapportMensuel(
            mois=mois_noms[mois - 1],
            annee=annee,
            type_nom=type_nom,
            operations=data["operations"],
            solde_final=solde_final,
            total_debits=data["total_debits"],
            total_credits=data["total_credits"]
        )
        rapports.append(rapport)
    
    return rapports

@router.get("/rapport/annuel/{annee}")
def get_rapport_annuel(
    annee: int,
    type_id: Optional[int] = None,
    afficher_solde: bool = False,
    db: Session = Depends(get_session)
):
    """
    Génère un rapport annuel détaillé par mois
    - Filtre par type si type_id est fourni
    - Affiche toutes les recettes de chaque mois
    - Affiche le solde à la fin de chaque mois
    Exemple: /rapport/annuel/2025?type_id=1
    """
    from calendar import monthrange
    
    mois_noms = [
        "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
        "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"
    ]
    
    rapport_annuel = {
        "annee": annee,
        "type": None,
        "rapports_mensuels": []
    }
    
    # Récupérer le nom du type si spécifié
    if type_id:
        type_obj = db.get(Type, type_id)
        if type_obj:
            rapport_annuel["type"] = {"id": type_id, "nom": type_obj.nom}
    
    for mois in range(1, 13):
        premier_jour = date(annee, mois, 1)
        dernier_jour = date(annee, mois, monthrange(annee, mois)[1])
        
        # Construire la requête pour le mois
        stmt = (
            select(Recette)
            .where(
                and_(
                    Recette.date >= premier_jour,
                    Recette.date <= dernier_jour
                )
            )
            .order_by(Recette.date, Recette.idRecette)
        )
        
        # Filtrer par type si spécifié
        if type_id:
            stmt = stmt.where(Recette.type_id == type_id)
        
        # Exclure les lignes avec libelle="solde" si demandé
        if not afficher_solde:
            stmt = stmt.where(
                (Recette.libelle == None) | 
                (Recette.libelle.ilike("%solde%") == False)
            )
        
        recettes_mois = db.exec(stmt).all()
        
        # Récupérer le solde à la fin du mois
        # (dernière recette du mois, tous types confondus pour avoir le vrai solde)
        stmt_solde = (
            select(Recette)
        .where(Recette.date < dernier_jour, Recette.type_id == type_id)
        .order_by(Recette.date.desc(), Recette.idRecette.desc())
        .limit(1)
        )
        derniere_recette = db.exec(stmt_solde).first()
        solde_fin_mois = derniere_recette.solde if derniere_recette else 0
        
        # Calculer les totaux du mois
        total_debits = sum(r.debit_montant for r in recettes_mois)
        total_credits = sum(r.credit_montant for r in recettes_mois)
        
        rapport_mensuel = {
            "mois": mois_noms[mois - 1],
            "numero_mois": mois,
            "nombre_operations": len(recettes_mois),
            "recettes": [
    {
        "idRecette": r.idRecette,
        "date": (r.date if i == 0 or r.date != recettes_mois[i-1].date else None),
        "libelle": r.libelle,
        "debit_montant": r.debit_montant,
        "credit_montant": r.credit_montant,
        "solde": r.solde,
        "type": {"id": r.type.idType, "nom": r.type.nom} if r.type else None
    }
    for i, r in enumerate(recettes_mois)
],

            "total_debits": total_debits,
            "total_credits": total_credits,
            "solde_fin_mois": solde_fin_mois
        }
        
        rapport_annuel["rapports_mensuels"].append(rapport_mensuel)
    
    return rapport_annuel
