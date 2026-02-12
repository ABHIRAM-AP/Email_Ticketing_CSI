from app.db import get_supabase
from app.models.registration import RegistrationCreate, RegistrationResponse
from app.utils.qr_generator import generate_qr_code, generate_ticket_id
from app.services.email_service import send_ticket_email
from datetime import datetime
from typing import Optional


class RegistrationService:
    def __init__(self):
        self.db = get_supabase()
    
    async def create_registration(self, registration: RegistrationCreate) -> dict:
        """
        Create a new registration and send ticket email
        
        Returns:
            Dict with registration details and ticket info
        """
        
        # 1. Check if event exists and is open for registration
        event = self.db.table('events').select('*').eq('id', registration.event_id).single().execute()
        
        if not event.data:
            raise ValueError("Event not found")
        
        if not event.data['registration_open']:
            raise ValueError("Registration is closed for this event")
        
        # 2. Check capacity
        current_count = self.db.table('registrations')\
            .select('id', count='exact')\
            .eq('event_id', registration.event_id)\
            .execute()
        
        if current_count.count >= event.data['capacity']:
            raise ValueError("Event is full")
        
        # 3. Check for duplicate registration (same email for same event)
        existing = self.db.table('registrations')\
            .select('id')\
            .eq('event_id', registration.event_id)\
            .eq('email', registration.email)\
            .execute()
        
        if existing.data:
            raise ValueError("You have already registered for this event")
        
        # 4. Create registration record (without ticket_id first)
        reg_data = {
            'event_id': registration.event_id,
            'name': registration.name,
            'email': registration.email,
            'phone': registration.phone,
            'college': registration.college,
            'checked_in': False
        }
        
        result = self.db.table('registrations').insert(reg_data).execute()
        
        if not result.data:
            raise ValueError("Failed to create registration")
        
        created_reg = result.data[0]
        
        # 5. Generate ticket ID and QR code
        ticket_id = generate_ticket_id(registration.event_id, created_reg['id'])
        qr_code = generate_qr_code(ticket_id)
        
        # 6. Update registration with ticket info
        self.db.table('registrations')\
            .update({'ticket_id': ticket_id, 'qr_code_url': qr_code})\
            .eq('id', created_reg['id'])\
            .execute()
        
        # 7. Send ticket email
        event_date_str = datetime.fromisoformat(event.data['event_date']).strftime('%B %d, %Y at %I:%M %p')
        
        email_sent = await send_ticket_email(
            recipient_email=registration.email,
            recipient_name=registration.name,
            event_name=event.data['name'],
            event_date=event_date_str,
            ticket_id=ticket_id,
            qr_code_base64=qr_code
        )
        
        return {
            'registration_id': created_reg['id'],
            'ticket_id': ticket_id,
            'qr_code_url': qr_code,
            'email_sent': email_sent,
            'event_name': event.data['name']
        }
    
    def get_registration_by_ticket(self, ticket_id: str) -> Optional[dict]:
        """Get registration details by ticket ID"""
        result = self.db.table('registrations')\
            .select('*, events(*)')\
            .eq('ticket_id', ticket_id)\
            .single()\
            .execute()
        
        return result.data if result.data else None
    
    def get_registrations_by_event(self, event_id: int) -> list:
        """Get all registrations for an event"""
        result = self.db.table('registrations')\
            .select('*')\
            .eq('event_id', event_id)\
            .order('created_at', desc=True)\
            .execute()
        
        return result.data