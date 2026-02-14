from fastapi import APIRouter, Depends,status,HTTPException
from sqlalchemy.orm import Session
from fastapi import HTTPException
from api.type.type_services import create_type,get_type
from api.type.type_model import type_create


from core.database import get_session

router = APIRouter()

@router.post("/create_type/")
def type_create(create_data:type_create,session : Session=Depends(get_session)):
    try:
        return create_type(create_data,session)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=str(e))
    
@router.get("/get_type/")
def get_types(session : Session=Depends(get_session)):
    try:
        return get_type(session)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=str(e))
