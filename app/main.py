from fastapi import FastAPI
from app import models
from app.database import engine
from app.routers import items_inventory, users, auth, items_sold
from fastapi.middleware.cors import CORSMiddleware

#models.Base.metadata.create_all(bind=engine)
from run_migrations import *

app = FastAPI()

origins = []

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)





app.include_router(items_inventory.router)
app.include_router(users.router)
app.include_router(auth.router)

app.include_router(items_sold.router)



@app.get("/")
async def root():
    return {"message": "Hello World"}
