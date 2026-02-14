from fastapi import APIRouter, Depends,status,HTTPException
from sqlalchemy.orm import Session
from fastapi import HTTPException
from api.montant.montant_model import montant_create
from api.montant.montant_services import create_montant,get_montant


from core.database import get_session

router = APIRouter()

@router.post("/create_montant/")
def montant_create(create_data:montant_create,session : Session=Depends(get_session)):
    try:
        return create_montant(create_data,session)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=str(e))
    
@router.get("/get_montant/")
def get_montants(session : Session=Depends(get_session)):
    try:
        return get_montant(session)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=str(e))
