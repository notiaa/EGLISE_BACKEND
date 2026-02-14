from fastapi import APIRouter
from api.type.type_routes import router as type_routes
from api.montant.montant_routes import router as montant_routes
from api.sortie.sortie_routes import router as sortie_routes
from api.entree.entree_routes import router as entree_routes
from api.detailEntree.detailEntree_routes import router as detailentree_routes
from api.recette.recette_routes import router as recette_routes
routers = APIRouter()

routers.include_router(type_routes, prefix="/types", tags=["Type"])
routers.include_router(montant_routes, prefix="/montant", tags=["Montant"])
routers.include_router(sortie_routes, prefix="/sortie", tags=["Sortie"])
routers.include_router(entree_routes, prefix="/entree", tags=["Entree"])
routers.include_router(detailentree_routes, prefix="/detailEntree", tags=["Detail Entree"])
routers.include_router(recette_routes, prefix="/recette", tags=["Recette"])


