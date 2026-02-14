from pydantic import BaseModel
from datetime import date
from typing import Optional

class entree_create(BaseModel):
    date:date
    montant:Optional[float]=0
    
class UpdateEntreeModel(BaseModel):
    date: Optional[date] = None
    montant: Optional[float] = 0

