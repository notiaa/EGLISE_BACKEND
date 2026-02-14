from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

class montant_create(BaseModel):
    montant:float