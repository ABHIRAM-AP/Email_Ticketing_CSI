import qrcode
import io
import base64
from typing import Optional


def generate_qr_code(data: str) -> str:
    """
    Generate QR code and return as base64 encoded string
    
    Args:
        data: String to encode in QR code (usually ticket_id)
    
    Returns:
        Base64 encoded PNG image string
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    print(img_str)
    
    return f"data:image/png;base64,{img_str}"


def generate_ticket_id(event_id: int, registration_id: int) -> str:
    """
    Generate unique ticket ID
    
    Format: EVT{event_id}-REG{registration_id}-{random}
    """
    import random
    import string
    
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    print( f"EVT{event_id:04d}-REG{registration_id:06d}-{random_str}")
    # return ( f"EVT{event_id:04d}-REG{registration_id:06d}-{random_str}")


