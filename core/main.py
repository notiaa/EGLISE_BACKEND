from datetime import datetime, timedelta

from fastapi import FastAPI

from core.database import init_db, get_session
# router
from api.routes.routes import routers
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()
    session = next(get_session())
    # generate_keys()

# ROUTES



from pathlib import Path

# Get the current file's path
current_dir = Path(__file__).resolve()

# Navigate up to the project root (adjust the number of parents as needed)
root_dir = current_dir.parents[1]  # Adjust '1' depending on how many levels up the root is
dr=datetime.now() + timedelta(days=2)

print(dr.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z')
app.include_router(routers)




