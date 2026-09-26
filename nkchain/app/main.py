from fastapi import FastAPI#this line imports fastapi's class
from sqlalchemy import text# added later to test whether the connection works


from app.database.connection import Base, engine# to test the connection? I don't know why, but it seems like the import didn't work properly.
from app.models import User, Wallet
#below two imports connect the routers to FastApi
from app.api.users import router as users_router
from app.api.wallets import router as wallets_router
from app.api.transfers import router as transfers_router


app = FastAPI(title = "nkchain")# this line creates the application object. Everything connects to this object. that is why this line is important.


Base.metadata.create_all(bind=engine)


app.include_router(users_router)
app.include_router(wallets_router)
app.include_router(transfers_router)


#This below block creates the first endpoint.
@app.get("/health")#when someone sends a GET request to /health, the function below is immediately run
def health_check():
    return {"status": "ok"}#this python dictionary is returned and automatically converted by FastAPI into JSON.



@app.get("/database-health")
def database_health_check():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))

    return {"database": result.scalar()}

#my fastapi application is now talking to postgresql.


#raw database-testing logic should not be permanently left in main.py