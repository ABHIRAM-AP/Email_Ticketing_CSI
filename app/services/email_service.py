from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
from app.config import settings
import base64


async def send_ticket_email(
    recipient_email: str,
    recipient_name: str,
    event_name: str,
    event_date: str,
    ticket_id: str,
    qr_code_base64: str
) -> bool:
    """
    Send ticket email with QR code using SendGrid HTTP API
    """
    
    try:
        print(f"📧 Preparing email for {recipient_email} via SendGrid API...")
        
        # HTML content
        html_content = f"""
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
        
        # Create message
        message = Mail(
            from_email=settings.email_from,
            to_emails=recipient_email,
            subject=f"🎫 Your Ticket for {event_name}",
            html_content=html_content
        )
        
        # Process QR code
        if 'base64,' in qr_code_base64:
            qr_data = qr_code_base64.split('base64,')[1]
        else:
            qr_data = qr_code_base64
        
        # Create attachment
        attachment = Attachment(
            FileContent(qr_data),
            FileName('ticket_qr_code.png'),
            FileType('image/png'),
            Disposition('attachment')
        )
        message.attachment = attachment
        
        print("✅ Message and attachment prepared")
        
        # Send via SendGrid HTTP API
        # API key is in EMAIL_PASSWORD environment variable
        sg = SendGridAPIClient(settings.email_password)
        response = sg.send(message)
        
        print(f"✅ Email sent successfully! Status: {response.status_code}")
        print(f"✅ Response body: {response.body}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error sending email: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False