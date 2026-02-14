from typing import List, Optional
from datetime import date, datetime

from pydantic import BaseModel


class RecetteCreate(BaseModel):
    date: date
    libelle: Optional[str] = None
    debit_montant: Optional[float] = 0
    credit_montant: Optional[float] = 0
    type_id: Optional[int] = None

class RecetteUpdate(BaseModel):
    date: Optional[date] = None
    libelle: Optional[str] = None
    debit_montant: Optional[float] = None
    credit_montant: Optional[float] = None
    type_id: Optional[int] = None
    solde:Optional[int]=None

class TypeResponse(BaseModel):
    idType: int
    nom: str

    class Config:
        orm_mode = True  # 👈 obligatoire pour que Pydantic accepte les objets ORM

class RecetteResponse(BaseModel):
    idRecette: int
    date: date
    libelle: Optional[str]
    debit_montant: float
    credit_montant: float
    solde: float
    type: Optional[TypeResponse]  # 👈 ici type est bien un dict

    class Config:
        orm_mode = True  # 👈 obligatoire pour que Pydantic accepte les objets ORM

class RapportMensuel(BaseModel):
    mois: str
    annee: int
    type_nom: str
    operations: List[RecetteResponse]
    solde_final: float
    total_debits: float
    total_credits: float