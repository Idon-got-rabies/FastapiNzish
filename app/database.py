from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import psycopg
from psycopg.rows import dict_row
import time
from app.config import settings
from dotenv import load_dotenv
import os

load_dotenv()

# while True:
#      try:
#          conn = psycopg.connect(host= settings.database_hostname, user= settings.database_username, dbname= settings.database_name,
#                             password= settings.database_password,row_factory=dict_row  )
#          cursor = conn.cursor()
#          print("Connected to database successfully")
#          break
#      except Exception as error:
#          print("Failed to connect to database")
#          print("Error:", error)
#          time.sleep(2)










SQLALCHEMY_DATABASE_URI = (f'postgresql://{settings.database_username}:{settings.database_password}'
                           f'@{settings.database_hostname}:{settings.database_port}/{settings.database_name}')

engine = create_engine(SQLALCHEMY_DATABASE_URI)

Sessionlocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = Sessionlocal()
    try:
        yield db
    finally:
        db.close()
