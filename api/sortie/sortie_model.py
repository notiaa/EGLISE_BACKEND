from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

class sortie_create(BaseModel):
    date_sortie:date
    montant:float
    raison:str