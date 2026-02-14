from sqlmodel import Session, select
from fastapi import HTTPException
from datetime import timedelta
from sqlmodel import Session, select,func,extract
from api.montant.montant_model import montant_create
from models.eglise_models import Montant
import logging
logging.basicConfig(level=logging.INFO)

def create_montant(montant: montant_create, session : Session):
    try:
        montant : Montant = Montant(montant=montant.montant)
        session.add(montant)
        session.commit()
        session.refresh(montant)
        return "insertion réussie"
    except Exception as e:
        return {"messageError": f"Error: {str(e)}"}


def get_montant(session:Session):
    try:
        type = session.exec(select(Montant)).all()
        return type
    except Exception as e:
        return {"messageError":f"{str(e)}"}