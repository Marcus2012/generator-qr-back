import qrcode
from io import BytesIO

def create_qr_code(data_url: str) -> bytes:
    """
    Toma una URL (ej. la de GCP) y genera la imagen del código QR en bytes (PNG).
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convertir a bytes para enviarlo directo como respuesta o subirlo
    img_byte_arr = BytesIO()
    img.save(img_byte_arr)
    return img_byte_arr.getvalue()
