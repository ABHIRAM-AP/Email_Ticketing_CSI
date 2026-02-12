import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from jinja2 import Template
import base64
from app.config import settings
from typing import Optional


async def send_ticket_email(
    recipient_email: str,
    recipient_name: str,
    event_name: str,
    event_date: str,
    ticket_id: str,
    qr_code_base64: str
) -> bool:
    """
    Send ticket email with QR code
    
    Args:
        recipient_email: Recipient's email
        recipient_name: Recipient's name
        event_name: Name of the event
        event_date: Event date string
        ticket_id: Unique ticket ID
        qr_code_base64: Base64 encoded QR code image
    
    Returns:
        True if email sent successfully, False otherwise
    """
    
    # Email HTML template
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                      color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
            .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
            .ticket-box { background: white; padding: 20px; margin: 20px 0; 
                         border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .qr-code { text-align: center; margin: 20px 0; }
            .qr-code img { max-width: 250px; border: 2px solid #667eea; padding: 10px; 
                          background: white; border-radius: 8px; }
            .info-row { margin: 10px 0; padding: 10px; background: #f0f0f0; border-radius: 4px; }
            .label { font-weight: bold; color: #667eea; }
            .footer { text-align: center; margin-top: 30px; color: #666; font-size: 12px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎉 Your Event Ticket</h1>
            </div>
            <div class="content">
                <h2>Hello {{ name }}!</h2>
                <p>Your registration for <strong>{{ event_name }}</strong> is confirmed!</p>
                
                <div class="ticket-box">
                    <div class="info-row">
                        <span class="label">Event:</span> {{ event_name }}
                    </div>
                    <div class="info-row">
                        <span class="label">Date:</span> {{ event_date }}
                    </div>
                    <div class="info-row">
                        <span class="label">Ticket ID:</span> {{ ticket_id }}
                    </div>
                    
                    <div class="qr-code">
                        <p><strong>Your QR Code Ticket</strong></p>
                        <img src="cid:qrcode" alt="QR Code">
                        <p style="font-size: 12px; color: #666;">
                            Please show this QR code at the event entrance
                        </p>
                    </div>
                </div>
                
                <p><strong>Important:</strong></p>
                <ul>
                    <li>Keep this email safe - you'll need it for check-in</li>
                    <li>Screenshot the QR code for quick access</li>
                    <li>Arrive 15 minutes before the event starts</li>
                </ul>
                
                <p>See you at the event! 🚀</p>
                
                <div class="footer">
                    <p>{{ app_name }}<br>
                    If you have any questions, please contact the event organizers.</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    try:
        # Render template
        template = Template(html_template)
        html_content = template.render(
            name=recipient_name,
            event_name=event_name,
            event_date=event_date,
            ticket_id=ticket_id,
            app_name=settings.app_name
        )
        
        # Create message
        message = MIMEMultipart('related')
        message['Subject'] = f"Your Ticket for {event_name}"
        message['From'] = settings.email_from
        message['To'] = recipient_email
        
        # Attach HTML content
        html_part = MIMEText(html_content, 'html')
        message.attach(html_part)
        
        # Attach QR code image
        # Remove data:image/png;base64, prefix if present
        qr_data = qr_code_base64.split(',')[1] if ',' in qr_code_base64 else qr_code_base64
        qr_image_data = base64.b64decode(qr_data)
        
        qr_image = MIMEImage(qr_image_data)
        qr_image.add_header('Content-ID', '<qrcode>')
        message.attach(qr_image)
        
        # Send email
        await aiosmtplib.send(
            message,
            hostname=settings.email_host,
            port=settings.email_port,
            username=settings.email_username,
            password=settings.email_password,
            start_tls=True
        )
        
        return True
        
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False