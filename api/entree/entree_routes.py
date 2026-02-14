import calendar
from pydoc import pager
from fastapi import APIRouter, Depends, Query, status, HTTPException
from fastapi.responses import FileResponse
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import A4,landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from sqlalchemy import Table
from sqlalchemy.orm import Session
from datetime import date, datetime
from fastapi import APIRouter, Query, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from pathlib import Path
from datetime import datetime
import tempfile
import os
from typing import List, Dict, Any

from api.entree.entree_services import (
    create_entree,
    get_balance_between_months,
    get_entree,
    get_balance_per_month,
    search_entree_or_sortie,
    get_balance_per_month_and_year,
    update_entree,
    delete_entree
)
from api.entree.entree_model import entree_create,UpdateEntreeModel
from core.database import get_session

router = APIRouter()

@router.post("/create_entree/")
def entree_create_route(create_data: entree_create, session: Session = Depends(get_session)):
    try:
        return create_entree(create_data, session)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    
@router.get("/get_entree/")
def get_entrees(session: Session = Depends(get_session)):
    try:
        return get_entree(session)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    
@router.get("/get_balance_per_months/")
def get_balance_per_months(start_time: date = None, end_time: date = None, session: Session = Depends(get_session), page: int = 1, number_items: int = 50):
    try:
        return get_balance_per_month(start_time, end_time, session, page, number_items)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    
@router.get("/search_entree_or_sortie/")
def search_entree_or_sorties(label: str, start_time: date = None, end_time: date = None, session: Session = Depends(get_session), page: int = 1, number_items: int = 50):
    try:
        return search_entree_or_sortie(label, start_time, end_time, session, page, number_items)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    
@router.get("/get_details_for_month_and_year/")
def get_details_for_month_and_years(month: int, year: int, session: Session = Depends(get_session)):
    try:
        return get_balance_per_month_and_year(month, year, session)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

# --- Nouvelle route pour UPDATE ---
@router.put("/update_entree/{entree_id}")
def update_entree_route(entree_id: str, update_data: UpdateEntreeModel, session: Session = Depends(get_session)):
    try:
        return update_entree(entree_id, update_data, session)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

# --- Nouvelle route pour DELETE ---
@router.delete("/delete_entree/{entree_id}")
def delete_entree_route(entree_id: str, session: Session = Depends(get_session)):
    try:
        return delete_entree(entree_id, session)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/balance/")
def read_balance(
    start_month: int = Query(..., ge=1, le=12),
    start_year: int = Query(..., ge=2000),
    end_month: int = Query(..., ge=1, le=12),
    end_year: int = Query(..., ge=2000),
    session: Session = Depends(get_session)
):
    try:
   # ou place la fonction dans ce fichier
        result = get_balance_between_months(start_month, start_year, end_month, end_year, session)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


@router.get("/balance/export_pdf/")
def export_balance_pdf(
    mois_debut: int = Query(...),
    annee_debut: int = Query(...),
    mois_fin: int = Query(...),
    annee_fin: int = Query(...),
    session: Session = Depends(get_session)
):
    result = get_balance_between_months(mois_debut, annee_debut, mois_fin, annee_fin, session)

    if not result or "data" not in result or not result["data"]:
        raise HTTPException(status_code=404, detail="Aucune donnée trouvée pour cette période")

    data_list = result["data"]

    data_dict = {}
    all_types = set()
    for row in data_list:
        key = (row["year"], row["month"])
        data_dict[key] = row
        for entree in row.get("entrees_by_type", []):
            all_types.add(entree["type"])

    all_types = sorted(all_types)
    all_columns = all_types + ["Total Sortie", "Balance"]

    all_months = []
    y, m = annee_debut, mois_debut
    while (y < annee_fin) or (y == annee_fin and m <= mois_fin):
        all_months.append((y, m))
        if m == 12:
            m = 1
            y += 1
        else:
            m += 1

    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    tmp_file.close()
    pdf_path = tmp_file.name

    doc = SimpleDocTemplate(pdf_path, pagesize=landscape(A4))
    elements = []
    styles = getSampleStyleSheet()
    elements.append(Paragraph(
        f"Balance détaillée entre {mois_debut:02d}/{annee_debut} et {mois_fin:02d}/{annee_fin}",
        styles["Title"]
    ))
    elements.append(Spacer(1, 20))

    # Préparer les données pour le tableau
    table_data = [["Mois/Année"] + all_columns]

    for year, month in all_months:
        month_name = calendar.month_name[month]
        row_data = data_dict.get((year, month))
        row = [f"{month_name} {year}"]

        if row_data:
            type_map = {t["type"]: t["total_entree"] for t in row_data.get("entrees_by_type", [])}
            for t in all_types:
                row.append(type_map.get(t, 0))
            row.append(row_data.get("total_sortie", 0))
            row.append(row_data.get("balance", 0))
        else:
            row += [0 for _ in all_columns]

        table_data.append(row)

    total_balance = sum(row_data.get("balance", 0) for row_data in data_list)
    total_row = ["Total Général"] + ["" for _ in all_types] + ["", total_balance]
    table_data.append(total_row)

    # Calculer largeur de chaque colonne pour occuper toute la page
    page_width, page_height = landscape(A4)
    col_count = len(table_data[0])
    # Petite marge de chaque côté
    margin = 20
    usable_width = page_width - 2 * margin
    col_widths = [usable_width / col_count for _ in range(col_count)]

    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#4F81BD")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,0), 12),
        ("GRID", (0,0), (-1,-1), 1, colors.black),
        ("BACKGROUND", (0,-1), (-1,-1), colors.HexColor("#D9EDF7")),
        ("FONTNAME", (0,-1), (-1,-1), "Helvetica-Bold")
    ]))

    elements.append(table)
    doc.build(elements)

    return FileResponse(pdf_path, media_type="application/pdf", filename="balance.pdf")