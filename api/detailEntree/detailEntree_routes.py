from fastapi import APIRouter, Depends,status,HTTPException
from sqlalchemy.orm import Session
from fastapi import HTTPException
from api.detailEntree.detailEntree_model import createEntree, detailEntree_Create
from api.detailEntree.detailEntree_services import create_details_entree,get_detailEntree,read_detail_entree


from core.database import get_session

router = APIRouter()

@router.post("/create_detailEntree/")
def detailEntree_create(create_data:createEntree,session : Session=Depends(get_session)):
    try:
        return create_details_entree(create_data,session)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=str(e))
    
@router.get("/get_detailEntree/")
def get_detailentrees(session : Session=Depends(get_session)):
    try:
        return get_detailEntree(session)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=str(e))
    
@router.get("/read_detail_entree/{idEntree}")
def read_detail_entrees(idEntree:str,session : Session=Depends(get_session)):
    try:
        return read_detail_entree(idEntree,session)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=str(e))
