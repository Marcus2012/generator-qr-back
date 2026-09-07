from typing import Optional
from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, File, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.db.models import QrCode, User
from app.schemas.qr import QrCodeResponse
from app.api.deps import get_current_active_user
from app.services.gcp_storage import generate_signed_url_for_blob, upload_pdf_to_gcs
from app.services.qr_generator import create_qr_code

router = APIRouter()

def _view_url(qr_id: int) -> str:
    return f"{settings.BACKEND_PUBLIC_URL}/api/qr/{qr_id}/view"

@router.post("/generate")
async def generate_qr_from_pdf(
    name: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Recibe un PDF, lo sube a Google Cloud Storage y devuelve la imagen del código QR
    que apunta a un enlace permanente de nuestro backend (no directamente a GCP,
    ya que las URLs firmadas caducan).
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="El archivo debe ser un PDF")

    content = await file.read()

    # Subir a GCP
    blob_name = upload_pdf_to_gcs(content, file.filename)
    if not blob_name:
        raise HTTPException(status_code=500, detail="Error al subir el archivo a GCP")

    # Guardar en el histórico
    qr_record = QrCode(name=name, blob_name=blob_name, owner_id=current_user.id)
    db.add(qr_record)
    db.commit()
    db.refresh(qr_record)

    # El QR apunta a nuestro propio endpoint, que firma una URL nueva en cada escaneo
    qr_image_bytes = create_qr_code(_view_url(qr_record.id))

    # Retornar la imagen directamente
    return Response(content=qr_image_bytes, media_type="image/png")

@router.get("/{qr_id}/view")
def view_qr_pdf(qr_id: int, db: Session = Depends(get_db)):
    """
    Endpoint público (sin autenticación): a este apuntan los QR impresos en los
    diplomas. Genera una URL firmada nueva y redirige, para que el enlace del QR
    nunca caduque aunque cada URL firmada individual sí lo haga.
    """
    qr_record = db.query(QrCode).filter(QrCode.id == qr_id).first()
    if not qr_record:
        raise HTTPException(status_code=404, detail="Código QR no encontrado")

    signed_url = generate_signed_url_for_blob(qr_record.blob_name)
    if not signed_url:
        raise HTTPException(status_code=500, detail="Error al generar el acceso al PDF")

    return RedirectResponse(signed_url)

@router.get("/history", response_model=list[QrCodeResponse])
def get_qr_history(
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Devuelve el histórico de códigos QR generados por el usuario autenticado,
    opcionalmente filtrado por nombre.
    """
    query = db.query(QrCode).filter(QrCode.owner_id == current_user.id)
    if search:
        query = query.filter(QrCode.name.ilike(f"%{search}%"))

    records = query.order_by(QrCode.created_at.desc()).all()
    return [
        QrCodeResponse(
            id=r.id, name=r.name, pdf_url=_view_url(r.id), created_at=r.created_at
        )
        for r in records
    ]
