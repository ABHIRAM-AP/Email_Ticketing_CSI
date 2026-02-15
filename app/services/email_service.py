import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import base64
from app.config import settings


async def send_ticket_email(
    recipient_email: str,
    recipient_name: str,
    event_name: str,
    event_date: str,
    ticket_id: str,
    qr_code_base64: str
) -> bool:
    """
    Send ticket email with QR code as attachment
    """
    
    try:
        print(f"📧 Preparing email for {recipient_email}...")
        
        # Create message
        msg = MIMEMultipart('mixed')
        msg['Subject'] = f"🎫 Your Ticket for {event_name}"
        msg['From'] = settings.email_from
        msg['To'] = recipient_email
        
        # HTML body
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
            border-radius: 10px 10px 0 0;
        }}
        .content {{
            background: #f9f9f9;
            padding: 30px;
            border-radius: 0 0 10px 10px;
        }}
        .ticket-box {{
            background: white;
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .info-row {{
            padding: 10px;
            margin: 8px 0;
            background: #f0f0f0;
            border-radius: 4px;
            border-left: 4px solid #667eea;
        }}
        .label {{
            font-weight: bold;
            color: #667eea;
        }}
        .alert {{
            background: #fff3cd;
            border: 2px solid #ffc107;
            border-radius: 8px;
            padding: 15px;
            margin: 20px 0;
        }}
        .alert strong {{
            color: #856404;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎉 Your Event Ticket</h1>
    </div>
    
    <div class="content">
        <h2>Hello {recipient_name}!</h2>
        <p>Your registration for <strong>{event_name}</strong> is confirmed!</p>
        
        <div class="ticket-box">
            <div class="info-row">
                <span class="label">Event:</span> {event_name}
            </div>
            <div class="info-row">
                <span class="label">Date:</span> {event_date}
            </div>
            <div class="info-row">
                <span class="label">Ticket ID:</span> {ticket_id}
            </div>
        </div>
        
        <div class="alert">
            <strong>📎 QR Code Attached!</strong>
            <p>Your ticket QR code is attached to this email as <strong>"ticket_qr_code.png"</strong></p>
            <ul>
                <li>Download the attachment</li>
                <li>Save it on your phone</li>
                <li>Show it at the event entrance</li>
            </ul>
        </div>
        
        <p><strong>Important:</strong></p>
        <ul>
            <li>Keep this email and attachment safe</li>
            <li>Arrive 15 minutes before the event</li>
            <li>Bring valid ID for verification</li>
        </ul>
        
        <p style="text-align: center; font-size: 18px; margin-top: 30px;">
            See you at the event! 🚀
        </p>
        
        <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 12px;">
            <p>{settings.app_name}</p>
            <p>Contact event organizers if you have questions</p>
        </div>
    </div>
</body>
</html>
        """
        
        print("✅ HTML body created")
        
        # Attach HTML body
        html_part = MIMEText(html, 'html', 'utf-8')
        msg.attach(html_part)
        
        print("✅ HTML attached")
        
        # Process QR code
        print(f"📊 QR code length: {len(qr_code_base64)}")
        print(f"📊 QR code starts with: {qr_code_base64[:50]}")
        
        if 'base64,' in qr_code_base64:
            qr_data = qr_code_base64.split('base64,')[1]
            print("✅ Removed data URL prefix")
        else:
            qr_data = qr_code_base64
            print("ℹ️  No prefix found, using as-is")
        
        # Decode to bytes
        try:
            qr_bytes = base64.b64decode(qr_data)
            print(f"✅ QR decoded successfully ({len(qr_bytes)} bytes)")
        except Exception as decode_error:
            print(f"❌ Base64 decode error: {decode_error}")
            raise
        
        # Attach as PNG file
        qr_attachment = MIMEApplication(qr_bytes, _subtype='png')
        qr_attachment.add_header('Content-Disposition', 'attachment', filename='ticket_qr_code.png')
        msg.attach(qr_attachment)
        
        print("✅ QR attachment added")
        
        # Send email
        print(f"📤 Sending email to {recipient_email}...")
        
        await aiosmtplib.send(
            msg,
            hostname=settings.email_host,
            port=settings.email_port,
            username=settings.email_username,
            password=settings.email_password,
            start_tls=True,
            timeout=10
        )
        
        print(f"✅ Email with QR attachment sent successfully to {recipient_email}")
        return True
        
    except Exception as e:
        print(f"❌ Error sending email: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False