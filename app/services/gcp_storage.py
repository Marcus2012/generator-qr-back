from datetime import timedelta
from google.cloud import storage
from google.oauth2 import service_account
from app.core.config import settings
import uuid
from typing import Optional

_credentials = service_account.Credentials.from_service_account_file(
    settings.GOOGLE_APPLICATION_CREDENTIALS
)

def _get_bucket():
    client = storage.Client(project=settings.GCP_PROJECT_ID, credentials=_credentials)
    return client.bucket(settings.GCP_BUCKET_NAME)

def upload_pdf_to_gcs(file_content: bytes, filename: str) -> Optional[str]:
    """
    Sube un archivo a Google Cloud Storage y retorna el nombre del blob (objeto).
    El bucket es privado: el nombre del blob se guarda para firmar una URL
    de acceso nueva cada vez que se necesite (ver generate_signed_url_for_blob),
    en vez de guardar una URL firmada que caduca.
    """
    try:
        # Generar un nombre único para evitar colisiones
        unique_filename = f"{uuid.uuid4()}_{filename}"

        blob = _get_bucket().blob(unique_filename)
        blob.upload_from_string(file_content, content_type="application/pdf")

        return unique_filename
    except Exception as e:
        print(f"Error subiendo a GCP: {e}")
        return None

def generate_signed_url_for_blob(blob_name: str, expiration_minutes: int = 15) -> Optional[str]:
    """
    Genera una URL firmada de corta duración para un blob ya existente.
    Se llama en cada escaneo/consulta, no al momento de subir el archivo.
    """
    try:
        blob = _get_bucket().blob(blob_name)
        return blob.generate_signed_url(
            version="v4",
            expiration=timedelta(minutes=expiration_minutes),
            method="GET",
        )
    except Exception as e:
        print(f"Error firmando URL de GCP: {e}")
        return None
