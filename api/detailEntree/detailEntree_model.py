from pydantic import BaseModel
from datetime import date, datetime
from typing import List, Optional

class detailEntree_Create(BaseModel):
    montant:float
    quantite:Optional[int]=0
    total:Optional[float]=0
    entree_id:Optional[str]=None
    type_id:int
class createEntree(BaseModel):
    entree:List[detailEntree_Create]


