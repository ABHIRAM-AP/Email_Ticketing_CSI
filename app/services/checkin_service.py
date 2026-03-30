from app.db import get_supabase
from app.services.csv_service import CSVService
from datetime import datetime
from typing import Optional, Dict


class CheckInService:
    def __init__(self):
        self.db = get_supabase()
        self.csv_service = CSVService()
    
    def check_in_by_qr(self, ticket_id: str) -> Dict:
        """
        Check-in using QR code (ticket ID)
        
        Returns:
            Dict with check-in result and participant info
        """
        HACKATHON_EVENT_ID = 1
        # 1. Find registration by ticket ID
        registration = self.db.table('registrations')\
            .select('*, events(*)')\
            .eq('ticket_id', ticket_id)\
            .single()\
            .execute()
        
        if not registration.data:
            return {
                'success': False,
                'message': 'Invalid ticket',
                'reason': 'not_found'
            }
        
        reg = registration.data
        
        # 2. Verify event matches
        if reg['event_id'] != HACKATHON_EVENT_ID:
            return {
                'success': False,
                'message': f"This ticket is for {reg['events']['name']}, not the Hackathon",
                'reason': 'wrong_event'
            }
        
        # 3. Check if already checked in
        if reg['checked_in']:
            return {
                'success': False,
                'message': f"Already checked in at {reg['checked_in_at']}",
                'reason': 'already_checked_in',
                'participant_name': reg['name'],
                'checked_in_at': reg['checked_in_at']
            }
        
        # 4. Mark as checked in
        self.db.table('registrations')\
            .update({'checked_in': True, 'checked_in_at': datetime.utcnow().isoformat()})\
            .eq('id', reg['id'])\
            .execute()
        
        # 5. Record in check_ins table
        check_in_data = {
            'event_id': HACKATHON_EVENT_ID,
            'email': reg['email'],
            'ticket_id': ticket_id,
            'source': 'qr'
        }
        self.db.table('check_ins').insert(check_in_data).execute()
        
        return {
            'success': True,
            'message': 'Check-in successful!',
            'participant_name': reg['name'],
            'email': reg['email'],
            'college': reg['college'],
            'event_name': reg['events']['name']
        }
    
    def check_in_by_email(self, email: str) -> Dict:
        """
        Check-in using email lookup (for hackathon participants)
        
        Returns:
            Dict with check-in result
        """
        HACKATHON_EVENT_ID = 1
        email = email.strip().lower()
        
        # 1. Check if email exists in hackathon participants
        is_hackathon = self.csv_service.check_participant_exists(email)
        
        if not is_hackathon:
            # Check if they have a regular ticket
            registration = self.db.table('registrations')\
                .select('*, events(*)')\
                .eq('email', email)\
                .eq('event_id', HACKATHON_EVENT_ID)\
                .execute()
            
            if not registration.data:
                return {
                    'success': False,
                    'message': 'Email not found in hackathon participants or event registrations',
                    'reason': 'not_found'
                }
            
            # They have a ticket, use QR check-in instead
            return {
                'success': False,
                'message': 'This participant has a ticket. Please use QR code scanner.',
                'reason': 'has_ticket'
            }
        
        # 2. Check if already checked in for this event
        existing_checkin = self.db.table('check_ins')\
            .select('*')\
            .eq('email', email)\
            .eq('event_id', HACKATHON_EVENT_ID)\
            .execute()
        
        if existing_checkin.data:
            return {
                'success': False,
                'message': f"Already checked in at {existing_checkin.data[0]['checked_in_at']}",
                'reason': 'already_checked_in',
                'checked_in_at': existing_checkin.data[0]['checked_in_at']
            }
        
        # 3. Get participant details
        participant = self.csv_service.get_participant_by_email(email)
        
        # 4. Record check-in
        check_in_data = {
            'event_id': HACKATHON_EVENT_ID,
            'email': email,
            'ticket_id': None,
            'source': 'csv'
        }
        self.db.table('check_ins').insert(check_in_data).execute()
        
        return {
            'success': True,
            'message': 'Check-in successful! (Hackathon participant - free entry)',
            'participant_name': participant['name'],
            'email': participant['email'],
            'college': participant.get('college'),
            'source': 'hackathon_csv'
        }
    
    def get_event_checkin_stats(self) -> Dict:
        """Get check-in statistics for the hackathon"""
        HACKATHON_EVENT_ID = 1
        
        # Total registrations (with tickets)
        registrations = self.db.table('registrations')\
            .select('id', count='exact')\
            .eq('event_id', HACKATHON_EVENT_ID)\
            .execute()
        
        # Checked in registrations
        checked_in_registrations = self.db.table('registrations')\
            .select('id', count='exact')\
            .eq('event_id', HACKATHON_EVENT_ID)\
            .eq('checked_in', True)\
            .execute()
        
        # Check-ins from CSV (hackathon participants)
        csv_checkins = self.db.table('check_ins')\
            .select('id', count='exact')\
            .eq('event_id', HACKATHON_EVENT_ID)\
            .eq('source', 'csv')\
            .execute()
        
        # All check-ins
        total_checkins = self.db.table('check_ins')\
            .select('id', count='exact')\
            .eq('event_id', HACKATHON_EVENT_ID)\
            .execute()
        
        # Get event details
        event = self.db.table('events')\
            .select('*')\
            .eq('id', HACKATHON_EVENT_ID)\
            .single()\
            .execute()
        
        return {
            'event_name': event.data['name'],
            'capacity': event.data['capacity'],
            'total_registrations': registrations.count,
            'checked_in_registrations': checked_in_registrations.count,
            'csv_checkins': csv_checkins.count,
            'total_checkins': total_checkins.count,
            'remaining_capacity': event.data['capacity'] - total_checkins.count
        }
    
    def get_recent_checkins(self, limit: int = 10) -> list:
        """Get recent check-ins for the hackathon"""
        HACKATHON_EVENT_ID = 1
        checkins = self.db.table('check_ins')\
            .select('*')\
            .eq('event_id', HACKATHON_EVENT_ID)\
            .order('checked_in_at', desc=True)\
            .limit(limit)\
            .execute()
        
        return checkins.data