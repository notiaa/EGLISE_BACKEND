
from models.eglise_models import Type
from sqlmodel import Session, select
from fastapi import HTTPException
from datetime import timedelta
from sqlmodel import Session, select,func,extract
from api.entree.entree_model import UpdateEntreeModel, entree_create
from api.sortie.sortie_services import get_detail_sortie_by_date

from models.eglise_models import Entree,generate_custom_id_entree,DetailEntree,Sortie
import logging
from models.Pagination import Pagination
from datetime import date, datetime
logging.basicConfig(level=logging.INFO)

def create_entree(entree: entree_create, session : Session):
    try:
        new_id=generate_custom_id_entree(session=session)
        charge : Entree = Entree(idEntree=new_id,date=entree.date,montant=0)
        session.add(charge)
        session.commit()
        session.refresh(charge)
        return charge
    except Exception as e:
        return {"messageError": f"Error: {str(e)}"}

def update_entree(entree_id: str, update_data: UpdateEntreeModel, session: Session):
    # Récupérer l'entrée existante
    entree = session.query(Entree).filter(Entree.idEntree == entree_id).first()
    if not entree:
        raise HTTPException(status_code=404, detail="Entrée non trouvée")
    # Mettre à jour les champs seulement s'ils sont fournis
    if update_data.date is not None:
        entree.date = update_data.date
    if update_data.montant is not None:
        entree.montant = update_data.montant

    session.commit()
    session.refresh(entree)
    return entree

def delete_entree(entree_id: str, session: Session):
    # Récupérer l'entrée existante
    entree = session.query(Entree).filter(Entree.idEntree == entree_id).first()
    if not entree:
        raise HTTPException(status_code=404, detail="Entrée non trouvée")
    
    # Supprimer l'entrée
    session.delete(entree)
    session.commit()
    
    return {"message": f"Entrée {entree_id} supprimée avec succès"}

def get_entree(session:Session):
    try:
        type = session.exec(select(Entree)).all()
        return type
    except Exception as e:
        return {"messageError":f"{str(e)}"}
def update_cp(id_entree:str,montant:float,session : Session):
    
    entree=session.exec(select(Entree).where(Entree.idEntree == id_entree)).first()
    if entree is None:
        raise Exception(f"CP  with id {id_entree} does not exist.")
    
    entree.montant=montant
    session.add(entree)
    session.commit()
    session.refresh(entree)
    return "Modification réussie"


def get_sum_identree(id_entree: str, session: Session):
    try:
        montants = session.exec(
            select(DetailEntree).where(DetailEntree.entree_id == id_entree)
        ).all()
        total_value = sum(m.total for m in montants)
        return total_value
    except Exception as e:
        return {"messageError": f"{str(e)}"}
    

def get_last_id(session:Session):
    statement = select(Entree.idEntree).order_by(Entree.idEntree.desc()).limit(1)
    result = session.exec(statement).first() 
    last_id = result
    return last_id

def get_sum_montant_entree(start_time: date = None, end_time: date = None, session: Session = None):
    query = select(
        extract('month', Entree.date).label("monthEntree"),
        extract('year', Entree.date).label("yearEntree"),
        func.sum(Entree.montant).label("montantEntree"),
        Entree.idEntree.label("idEntree"),
    ).group_by("monthEntree", "yearEntree").order_by("yearEntree", "monthEntree")
    if start_time:
        query = query.where(Entree.date >= start_time)
    if end_time:
        query = query.where(Entree.date <= end_time)

    result = session.exec(query).all()
    return result

def search_entree_or_sortie(label: str, start_time: date = None, end_time: date = None, session: Session = None, page: int = 1, number_items: int = 50):
    try:
        pagination = Pagination(page=page, limit=number_items)
        query = None
        count = None
        if label is not None:
            if label and label.upper() == "STR":
                query = select(
                    Sortie.date.label("dateSortie"),
                    Sortie.idSortie.label("idSortie"),
                    Sortie.montant.label("montantSortie"),
                    Sortie.raison.label("raison")
                )
                count = select(func.count(Sortie.idSortie))
                if start_time is not None and end_time is not None:
                    query = query.where(Sortie.date.between(start_time, end_time))
                    count = count.where(Sortie.date.between(start_time, end_time))
                elif start_time is not None:
                    query = query.where(Sortie.date == start_time)
                    count = count.where(Sortie.date == start_time)
                elif end_time is not None:
                    query = query.where(Sortie.date == end_time)
                    count = count.where(Sortie.date == end_time)
            elif label and label.upper() == 'ETR':
                query = select(
                    Entree.date.label("dateEntree"),
                    Entree.idEntree.label("idEntree"),
                    Entree.montant.label("montantEntree")
                )
                count = select(func.count(Entree.idEntree))
                if start_time is not None and end_time is not None:
                    query = query.where(Entree.date.between(start_time, end_time))
                    count = count.where(Entree.date.between(start_time, end_time))
                elif start_time is not None:
                    query = query.where(Entree.date == start_time)
                    count = count.where(Entree.date == start_time)
                elif end_time is not None:
                    query = query.where(Entree.date == end_time)
                    count = count.where(Entree.date == end_time)

            query = query.offset(pagination.offset).limit(pagination.limit)  # Appliquer la pagination
            result = session.exec(query).all()
            c = session.exec(count).first()

            # Formatter le résultat en liste de dictionnaires
            formatted_result = [
                {
                    "dateEntree": row.dateEntree if label.upper() == "ETR" else row.dateSortie,
                    "idEntree": row.idEntree if label.upper() == "ETR" else row.idSortie,
                    "montantEntree": row.montantEntree if label.upper() == "ETR" else row.montantSortie,
                    "raison": row.raison if label.upper() == "STR" else None
                }
                for row in result
            ]

        pagination.total_items = c
        return {"data": formatted_result, "pagination": pagination.dict()}

    except Exception as e:
        return {"messageError": f"Error: {str(e)}"}

def get_balance_per_month(start_time: date = None, end_time: date = None, session: Session = None, page: int = 1, number_items: int = 50):
    try:
        pagination = Pagination(page=page, limit=number_items)
        entree_query = select(
            extract('month', Entree.date).label("month"),
            extract('year', Entree.date).label("year"),
            func.coalesce(func.sum(Entree.montant), 0).label("total_entree")
        ).group_by(extract('year', Entree.date), extract('month', Entree.date)).alias("entrees")
        sortie_query = select(
            extract('month', Sortie.date).label("month"),
            extract('year', Sortie.date).label("year"),
            func.coalesce(func.sum(Sortie.montant), 0).label("total_sortie")
        ).group_by(extract('year', Sortie.date), extract('month', Sortie.date)).alias("sorties")
        query = select(
            entree_query.c.month,
            entree_query.c.year,
            entree_query.c.total_entree,
            sortie_query.c.total_sortie,
            (entree_query.c.total_entree - sortie_query.c.total_sortie).label("balance")
        ).outerjoin(
            sortie_query, 
            (entree_query.c.month == sortie_query.c.month) & (entree_query.c.year == sortie_query.c.year)
        ).order_by(entree_query.c.year, entree_query.c.month)
        if start_time:
            query = query.where(entree_query.c.year >= start_time.year, entree_query.c.month >= start_time.month)
        if end_time:
            query = query.where(entree_query.c.year <= end_time.year, entree_query.c.month <= end_time.month)
        count_query = select(func.count().label("total_count")).select_from(entree_query)
        c = session.exec(count_query).first()
        result = session.exec(query).all()
        formatted_result = [
            {
                "month": row.month,
                "year": row.year,
                "total_entree": row.total_entree,
                "total_sortie": row.total_sortie if row.total_sortie is not None else 0,
                "balance": row.balance if row.balance is not None else 0
            }
            for row in result
        ]
        pagination.total_items = c
        return {"data": formatted_result, "pagination": pagination.dict()}

    except Exception as e:
        return {"messageError": f"Error: {str(e)}"}
    
def get_balance_per_month_and_year(month: int = None, year: int = None, session: Session = None):
    try:
        # Entrées par type, mois et année
        entree_query = (
            select(
                DetailEntree.type_id.label("type_id"),
                extract('month', Entree.date).label("month"),
                extract('year', Entree.date).label("year"),
                func.coalesce(func.sum(DetailEntree.total), 0).label("total_entree")
            )
            .join(Entree, DetailEntree.entree_id == Entree.idEntree)
            .group_by(DetailEntree.type_id, extract('year', Entree.date), extract('month', Entree.date))
        )

        # Sorties par mois et année
        sortie_query = (
            select(
                extract('month', Sortie.date).label("month"),
                extract('year', Sortie.date).label("year"),
                func.coalesce(func.sum(Sortie.montant), 0).label("total_sortie")
            )
            .group_by(extract('year', Sortie.date), extract('month', Sortie.date))
        )

        if month:
            entree_query = entree_query.where(extract('month', Entree.date) == month)
            sortie_query = sortie_query.where(extract('month', Sortie.date) == month)
        if year:
            entree_query = entree_query.where(extract('year', Entree.date) == year)
            sortie_query = sortie_query.where(extract('year', Sortie.date) == year)

        # Exécuter les requêtes
        entrees = session.exec(entree_query).all()
        sorties = session.exec(sortie_query).all()

        # Construire le résultat
        result = {}
        for e in entrees:
            key = (int(e.year), int(e.month))
            if key not in result:
                result[key] = {
                    "month": int(e.month),
                    "year": int(e.year),
                    "total_sortie": 0,
                    "total_entree": 0,  # Nouveau champ pour le total des entrées
                    "entrees_by_type": []
                }
            result[key]["entrees_by_type"].append({
                "type_id": e.type_id,
                "total_entree": e.total_entree
            })
            result[key]["total_entree"] += e.total_entree  # Ajouter à total_entree global

        for s in sorties:
            key = (int(s.year), int(s.month))
            if key not in result:
                result[key] = {
                    "month": int(s.month),
                    "year": int(s.year),
                    "total_sortie": s.total_sortie,
                    "total_entree": 0,
                    "entrees_by_type": []
                }
            else:
                result[key]["total_sortie"] = s.total_sortie

        # Calculer balance par mois
        for k, v in result.items():
            v["balance"] = v["total_entree"] - v["total_sortie"]

        # Trier par année et mois
        sorted_result = sorted(result.values(), key=lambda x: (x["year"], x["month"]))

        return {"data": sorted_result}

    except Exception as e:
        return {"messageError": str(e)}
    

def get_balance_between_months(
    start_month: int, start_year: int,
    end_month: int, end_year: int,
    session: Session
):
    try:
        # Entrées
        entree_query = (
            select(
                DetailEntree.type_id,
                extract('month', Entree.date).label("month"),
                extract('year', Entree.date).label("year"),
                func.coalesce(func.sum(DetailEntree.total), 0).label("total_entree")
            )
            .join(Entree, DetailEntree.entree_id == Entree.idEntree)
            .where(
                (extract('year', Entree.date) > start_year) |
                ((extract('year', Entree.date) == start_year) & (extract('month', Entree.date) >= start_month))
            )
            .where(
                (extract('year', Entree.date) < end_year) |
                ((extract('year', Entree.date) == end_year) & (extract('month', Entree.date) <= end_month))
            )
            .group_by(DetailEntree.type_id, extract('year', Entree.date), extract('month', Entree.date))
        )

        # Sorties
        sortie_query = (
            select(
                extract('month', Sortie.date).label("month"),
                extract('year', Sortie.date).label("year"),
                func.coalesce(func.sum(Sortie.montant), 0).label("total_sortie")
            )
            .where(
                (extract('year', Sortie.date) > start_year) |
                ((extract('year', Sortie.date) == start_year) & (extract('month', Sortie.date) >= start_month))
            )
            .where(
                (extract('year', Sortie.date) < end_year) |
                ((extract('year', Sortie.date) == end_year) & (extract('month', Sortie.date) <= end_month))
            )
            .group_by(extract('year', Sortie.date), extract('month', Sortie.date))
        )

        entrees = session.exec(entree_query).all()
        sorties = session.exec(sortie_query).all()

        # Lier type_id avec nomType
        type_dict = {t.idType: t.nom for t in session.exec(select(Type)).all()}

        # Construire le résultat
        result = {}
        for e in entrees:
            key = (int(e.year), int(e.month))
            if key not in result:
                result[key] = {
                    "month": int(e.month),
                    "year": int(e.year),
                    "total_sortie": 0,
                    "total_entree": 0,
                    "entrees_by_type": []
                }
            result[key]["entrees_by_type"].append({
                "type": type_dict.get(e.type_id, "Inconnu"),
                "total_entree": e.total_entree
            })
            result[key]["total_entree"] += e.total_entree

        for s in sorties:
            key = (int(s.year), int(s.month))
            if key not in result:
                result[key] = {
                    "month": int(s.month),
                    "year": int(s.year),
                    "total_sortie": s.total_sortie,
                    "total_entree": 0,
                    "entrees_by_type": []
                }
            else:
                result[key]["total_sortie"] = s.total_sortie

        # Calcul balance
        total_general_balance = 0
        for v in result.values():
            v["balance"] = v["total_entree"] - v["total_sortie"]
            total_general_balance += v["balance"]

        # Trier
        sorted_result = sorted(result.values(), key=lambda x: (x["year"], x["month"]))
        
        return {
            "data": sorted_result,
            "total_general_balance": total_general_balance
        }
    except Exception as e:
        return {"messageError": str(e)}
