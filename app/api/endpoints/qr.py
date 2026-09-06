from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Response
from app.db.models import User
from app.api.deps import get_current_active_user
from app.services.gcp_storage import upload_pdf_to_gcs
from app.services.qr_generator import create_qr_code

router = APIRouter()

@router.post("/generate")
async def generate_qr_from_pdf(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    """
    Recibe un PDF, lo sube a Google Cloud Storage y devuelve la imagen del código QR
    que apunta a la URL de GCP.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="El archivo debe ser un PDF")
        
    content = await file.read()
    
    # Subir a GCP
    gcp_url = upload_pdf_to_gcs(content, file.filename)
    if not gcp_url:
        raise HTTPException(status_code=500, detail="Error al subir el archivo a GCP")
        
    # Generar QR
    qr_image_bytes = create_qr_code(gcp_url)
    
    # Retornar la imagen directamente
    return Response(content=qr_image_bytes, media_type="image/png")
