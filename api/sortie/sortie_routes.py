from fastapi import APIRouter, Depends,status,HTTPException
from sqlalchemy.orm import Session
from fastapi import HTTPException
from api.sortie.sortie_model import sortie_create
from api.sortie.sortie_services import create_sortie,get_sortie,get_detail_sortie


from core.database import get_session

router = APIRouter()

@router.post("/create_sortie/")
def sortie_create(create_data:sortie_create,session : Session=Depends(get_session)):
    try:
        return create_sortie(create_data,session)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=str(e))
    
@router.get("/get_sortie/")
def get_sorties(session : Session=Depends(get_session)):
    try:
        return get_sortie(session)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=str(e))
    
@router.get("/get_detail_sortie/{idSortie}")
def get_detail_sorties(idSortie:str,session : Session=Depends(get_session)):
    try:
        return get_detail_sortie(idSortie,session)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=str(e))
