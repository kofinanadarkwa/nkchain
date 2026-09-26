import os #gives python access to environment variables

from dotenv import load_dotenv #imports the function that reads the .env file
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker #sessionmaker allows database sessions to be created
#DeclarativeBase is imported so that all of the database models can inherit from a common SQLAlchemy base.


load_dotenv()# loads DATABASE_URL into the environment

DATABASE_URL = os.getenv("DATABASE_URL") # this code makes python retrieve the database URL

engine = create_engine(DATABASE_URL) # this line creates the SQLAlchemy engine
#the engine is the main mechanism that SQLALchemy uses to talk with PostgreSQl



class Base(DeclarativeBase):#this is the foundation for the database models
    pass# This block of code is an example of class inheritance since Base inherits from DeclarativeBase. It uses "pass" as its core logic because it doesn't need to have any additional functions other than being a child class of DeclarativeBase



SessionLocal = sessionmaker(
    autocommit = False,
    autoflush = False,
    bind = engine
)#A user created object to create database sessions that is built on the sessionmaker class from sqlalchemy.orm


#TO create a database dependency
def get_db():
    db = SessionLocal()

    try:
        yield db #I used yield because "return" would make the code below this line unable to run. And yield is more suited in case errors happen.

    finally:
        db.close()# I decided to not print an 'except' after the 'try' because 'finally' already handles what I want to do.

#this above snippet of code allows an API request to get a database session

#above code to be used later with FastApi's dependency injection system


