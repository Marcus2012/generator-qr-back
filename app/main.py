from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import auth, users, qr

app = FastAPI(
    title="Generador QR Backend",
    description="API para subir PDFs a GCP y generar códigos QR con autenticación.",
    version="1.0.0"
)

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar Routers
app.include_router(auth.router, tags=["Autenticación"])
app.include_router(users.router, prefix="/api/users", tags=["Usuarios"])
app.include_router(qr.router, prefix="/api/qr", tags=["Códigos QR"])

@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API del Generador de Códigos QR"}
