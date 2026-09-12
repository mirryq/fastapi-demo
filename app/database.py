from sqlmodel import Session, create_engine
from typing import Annotated
from fastapi import Depends
from app.config import settings
# import psycopg
# from psycopg.rows import dict_row
# import time

SQLALCHEMY_DATABASE_URL = f'postgresql+psycopg://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}'
engine = create_engine(SQLALCHEMY_DATABASE_URL)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


# connecting to database without ORM
# while True:
#     try:
#         conn = psycopg.connect(
#             host='localhost', dbname='fastapi-demo', user='postgres', password='8q2m4r', row_factory=dict_row)
#         cursor = conn.cursor()
#         print("Database connection was successful")
#         break
#     except Exception as error:
#         print("Connecting to database failed")
#         print("Error: ", error)
#         time.sleep(2)
