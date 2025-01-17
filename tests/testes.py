# type: ignore


import time

import pyodbc
from sqlalchemy import create_engine
from sqlalchemy.sql import text

# Variáveis de acesso
driver = "ODBC Driver 17 for SQL Server"
server = "192.168.0.21"
database = "Stanley_000_CRM"
username = "rcoelho"
password = "nb@2345"
table = "TB_RESULTADO_CAMPANHA_HISTORICO"
sql_query = f"SELECT TOP 1000 * FROM {table}"

engine = f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver={driver.replace(' ', '+')}"
print(engine)
print(
    "mssql+pyodbc://nbbi:nb#1010@192.168.0.21/Ambev_010_CBE_BI?driver=ODBC+Driver+17+for+SQL+Server"
)


def data_insert():
    connection_string = f"mssql+pyodbc://nbbi:nb#1010@192.168.0.21/Ambev_010_CBE_BI?driver=ODBC+Driver+17+for+SQL+Server"

    engine = create_engine(
        connection_string,
        pool_size=10,  # Número máximo de conexões na pool
        max_overflow=20,  # Número de conexões adicionais permitidas
        pool_timeout=30,  # Tempo de espera para uma conexão
        pool_pre_ping=True,  # Verifica se a conexão está ativa antes de usá-la
    )


data_insert()
