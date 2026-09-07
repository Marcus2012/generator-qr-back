import os
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from dotenv import load_dotenv

load_dotenv()

# We try to use DATABASE_URL if present, otherwise we build it
# Note: config uses aiomysql in .env but for testing we can use pymysql
db_url = os.getenv("DATABASE_URL")
if db_url and "aiomysql" in db_url:
    db_url = db_url.replace("aiomysql", "pymysql")

if not db_url:
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "secret")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "3306")
    db_name = os.getenv("DB_NAME", "qr_backend")
    db_url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}"

print(f"Probando conexión a: {db_url}")

try:
    engine = create_engine(db_url)
    with engine.connect() as connection:
        print("¡Conexión exitosa a la base de datos!")
except OperationalError as e:
    print("Error de conexión. Detalles:")
    print(e)
except Exception as e:
    print("Ocurrió un error inesperado:")
    print(e)
