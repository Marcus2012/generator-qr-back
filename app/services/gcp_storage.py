from google.cloud import storage
from app.core.config import settings
import uuid
from typing import Optional

def upload_pdf_to_gcs(file_content: bytes, filename: str) -> Optional[str]:
    """
    Sube un archivo a Google Cloud Storage y retorna su URL pública.
    Requiere que GOOGLE_APPLICATION_CREDENTIALS esté configurado en el entorno.
    """
    try:
        # Generar un nombre único para evitar colisiones
        unique_filename = f"{uuid.uuid4()}_{filename}"
        
        client = storage.Client(project=settings.GCP_PROJECT_ID)
        bucket = client.bucket(settings.GCP_BUCKET_NAME)
        blob = bucket.blob(unique_filename)
        
        # Subir el archivo
        blob.upload_from_string(file_content, content_type="application/pdf")
        
        # Opcional: Hacer el archivo público si el bucket lo permite
        # blob.make_public() 
        # return blob.public_url

        # Alternativa: generar URL firmada o retornar URL de acceso
        # return blob.generate_signed_url(expiration=timedelta(days=7))
        
        # Para propósitos de este backend, devolveremos el link público asumiendo bucket público
        return f"https://storage.googleapis.com/{settings.GCP_BUCKET_NAME}/{unique_filename}"
    except Exception as e:
        print(f"Error subiendo a GCP: {e}")
        return None
