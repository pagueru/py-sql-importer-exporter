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

# Benchmark PyODBC
start_time = time.time()

conn = pyodbc.connect(
    f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};UID={username};PWD={password}"
)
cursor = conn.cursor()
cursor.execute(sql_query)
rows = cursor.fetchall()

end_time = time.time()
pyodbc_time = end_time - start_time
print(f"PyODBC: {pyodbc_time} seconds")

cursor.close()
conn.close()

# Benchmark SQLAlchemy
start_time = time.time()

engine = create_engine(
    f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver={driver.replace(' ', '+')}"
)
connection = engine.connect()
result = connection.execute(text(sql_query))
rows = result.fetchall()

end_time = time.time()
sqlalchemy_time = end_time - start_time
print(f"SQLAlchemy: {sqlalchemy_time} seconds")

connection.close()

# Escrever tempos em um arquivo .txt
with open("./tests/benchmark_times.txt", "w", encoding="utf-8") as file:
    file.write(f"PyODBC: {pyodbc_time} seconds\n")
    file.write(f"SQLAlchemy: {sqlalchemy_time} seconds\n")
