
from sqlmodel import Session, select
from fastapi import HTTPException
from datetime import timedelta
from sqlmodel import Session, select,func,extract
from api.sortie.sortie_model import sortie_create
from models.eglise_models import Sortie,generate_custom_id_sortie
from datetime import date, datetime
import logging
logging.basicConfig(level=logging.INFO)

def create_sortie(sortie: sortie_create, session : Session):
    try:
        new_id=generate_custom_id_sortie(session=session)
        sortie : Sortie = Sortie(idSortie=new_id,date=sortie.date_sortie,montant=sortie.montant,raison=sortie.raison)
        session.add(sortie)
        session.commit()
        session.refresh(sortie)
        return "insertion réussie"
    except Exception as e:
        return {"messageError": f"Error: {str(e)}"}


def get_sortie(session:Session):
    try:
        type = session.exec(select(Sortie)).all()
        return type
    except Exception as e:
        return {"messageError":f"{str(e)}"}
    
    
def get_sum_montant_sortie(start_time: date = None, end_time: date = None, session: Session = None):
    query = select(
        extract('month', Sortie.date).label("monthSortie"),
        extract('year', Sortie.date).label("yearSortie"),
        func.sum(Sortie.montant).label("montantSortie"),
        Sortie.idSortie.label("idSortie")
    ).group_by("monthSortie", "yearSortie").order_by("yearSortie", "monthSortie")
    if start_time:
        query = query.where(Sortie.date >= start_time)
    if end_time:
        query = query.where(Sortie.date <= end_time)

    result = session.exec(query).all()
    return result

def get_detail_sortie(id_Sortie: str, session: Session = None):
    # Effectuer la requête sur la base de données pour récupérer les informations de la sortie
    query = session.exec(select(
        Sortie.idSortie.label("idSortie"),
        Sortie.date.label("dateSortie"),
        Sortie.montant.label("montantSortie"),
        Sortie.raison.label("raison")
    ).where(Sortie.idSortie == id_Sortie)).all()

    # Formatter le résultat comme une liste de dictionnaires
    formatted_result = [
        {
            "idSortie": row.idSortie,
            "dateSortie": row.dateSortie,
            "montantSortie": row.montantSortie,
            "raison": row.raison
        }
        for row in query
    ]

    return formatted_result

def get_detail_sortie_by_date(month: int, year: int, session: Session):
    query = session.exec(select(
        Sortie.idSortie.label("idSortie"),
        Sortie.date.label("dateSortie"),
        Sortie.montant.label("montantSortie"),
        Sortie.raison.label("raison")
    ).where(
        extract('month', Sortie.date) == month,
        extract('year', Sortie.date) == year
    )).all()

    formatted_result = [
        {
            "idSortie": row.idSortie,
            "dateSortie": row.dateSortie,
            "montantSortie": row.montantSortie,
            "raison": row.raison
        }
        for row in query
    ]

    return formatted_result





    