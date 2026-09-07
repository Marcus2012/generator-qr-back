from datetime import datetime
from pydantic import BaseModel

class QrCodeResponse(BaseModel):
    id: int
    name: str
    pdf_url: str
    created_at: datetime

    class Config:
        from_attributes = True
