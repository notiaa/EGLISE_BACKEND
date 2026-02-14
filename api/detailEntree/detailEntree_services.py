
from sqlmodel import Session, select
from fastapi import HTTPException
from datetime import timedelta
from sqlmodel import Session, select,func,extract
from api.detailEntree.detailEntree_model import createEntree, detailEntree_Create
from models.eglise_models import DetailEntree,Type,Entree
import logging
from api.entree.entree_services import get_sum_identree,update_cp,get_last_id
logging.basicConfig(level=logging.INFO)

def create_details_entree(details: createEntree, session: Session):
    try:
        # Récupérer l'id de l'entree globale
        id_entree = get_last_id(session=session)

        for detail in details.entree:
            # Calculer le total pour chaque détail
            total_calcul = calcul_detail_entree(montant=detail.montant, quantite=detail.quantite)
            charge = DetailEntree(
                entree_id=id_entree,
                type_id=detail.type_id,
                montant=detail.montant,
                quantite=detail.quantite,
                total=total_calcul
            )
            session.add(charge)

        # Commit de tous les détails
        session.commit()

        # Refresh si besoin
        # session.flush()
        # session.refresh(charge)

        # Calculer le montant total pour l'entree globale
        montant_total = get_sum_identree(id_entree, session=session)
        print(montant_total)
        update_cp(id_entree, montant=montant_total, session=session)

        return {"message": "Insertion réussie", "entree_id": id_entree}

    except Exception as e:
        session.rollback()  # rollback en cas d'erreur
        return {"messageError": f"Error: {str(e)}"}


def get_detailEntree(session:Session):
    try:
        type = session.exec(select(DetailEntree)).all()
        return type
    except Exception as e:
        return {"messageError":f"{str(e)}"}
    
def calcul_detail_entree(montant:float,quantite:int):
    total=montant*quantite
    return total


def read_detail_entree(id_entree: str, session: Session):
    # Requête pour obtenir les détails de l'entree avec un total global
    result = session.exec(
        select(
            DetailEntree.entree_id.label("idEntree"),
            DetailEntree.montant.label("montantDetailEntree"),
            DetailEntree.quantite.label("quantiteDetailEntree"),
            DetailEntree.total.label("totalDetail"),
            Type.nom.label("type"),
            func.sum(DetailEntree.total).over(partition_by=[Type.nom]).label("totalDetailGlobal")  
        )
        .join(Type, Type.idType == DetailEntree.type_id)
        .where(DetailEntree.entree_id == id_entree)  
    ).all()

    if not result:
        raise Exception(f"Entree with id {id_entree} does not exist.")

    # Formater le résultat sous forme de liste de dictionnaires
    formatted_result = [
        {
            "idEntree": row.idEntree,
            "montantDetailEntree": row.montantDetailEntree,
            "quantiteDetailEntree": row.quantiteDetailEntree,
            "totalDetail": row.totalDetail,
            "totalDetailGlobal": row.totalDetailGlobal,  # Ajouter le total global
            "type": row.type
        }
        for row in result
    ]

    return formatted_result


def read_detail_entree_by_date(month: int, year: int, session: Session):
    result = session.exec(
        select(
            extract('day', Entree.date).label("day"),
            DetailEntree.entree_id.label("idEntree"),
            DetailEntree.montant.label("montantDetailEntree"),
            DetailEntree.quantite.label("quantiteDetailEntree"),
            DetailEntree.total.label("totalDetail"),
            Type.nom.label("type"),
            func.sum(DetailEntree.total).over(partition_by=[Type.nom]).label("totalDetailGlobal")
        )
        .join(Type, Type.idType == DetailEntree.type_id)
        .join(Entree,Entree.idEntree==DetailEntree.entree_id)
        .where(
            extract('month', Entree.date) == month,
            extract('year', Entree.date) == year
        )
        .group_by(
            extract('day', Entree.date), 
            DetailEntree.entree_id, 
            DetailEntree.montant, 
            DetailEntree.quantite, 
            DetailEntree.total, 
            Type.nom
        )
        .order_by(extract('day', Entree.date))
    ).all()

    day_details = []
    current_day = None
    current_day_details = []

    for entry in result:
        day = entry.day
        if day != current_day:
            if current_day is not None:
                day_details.append({"day": current_day, "details": current_day_details})
            current_day = day
            current_day_details = []
        current_day_details.append({
            "idEntree": entry.idEntree,
            "montantDetailEntree": entry.montantDetailEntree,
            "quantiteDetailEntree": entry.quantiteDetailEntree,
            "totalDetail": entry.totalDetail,
            "totalDetailGlobal": entry.totalDetailGlobal,
            "type": entry.type
        })

    # Ajouter les détails du dernier jour
    if current_day is not None:
        day_details.append({"day": current_day, "details": current_day_details})

    return day_details


    
    


    