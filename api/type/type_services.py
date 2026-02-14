
from sqlmodel import Session, select
from fastapi import HTTPException
from datetime import timedelta
from sqlmodel import Session, select,func,extract
from api.type.type_model import type_create
from models.eglise_models import Type
import logging
logging.basicConfig(level=logging.INFO)

def create_type(type: type_create, session : Session):
    try:
        charge : Type = Type(nom=type.nom)
        session.add(charge)
        session.commit()
        session.refresh(charge)
        return "insertion réussie"
    except Exception as e:
        return {"messageError": f"Error: {str(e)}"}


def get_type(session:Session):
    try:
        type = session.exec(select(Type)).all()
        return type
    except Exception as e:
        return {"messageError":f"{str(e)}"}
    
    


    