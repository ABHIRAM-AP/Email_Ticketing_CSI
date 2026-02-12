import csv
import io
from typing import List, Dict
from app.db import get_supabase
from app.models.checkin import HackathonParticipantCreate
from email_validator import validate_email, EmailNotValidError


class CSVService:
    def __init__(self):
        self.db = get_supabase()
    
    def parse_csv(self, file_content: bytes) -> Dict:
        """
        Parse CSV file and import hackathon participants
        
        Expected CSV columns: name, email, college, phone
        Or just: email (minimum)
        
        Returns:
            Dict with import statistics
        """
        results = {
            'total_rows': 0,
            'imported': 0,
            'duplicates': 0,
            'errors': 0,
            'error_details': []
        }
        
        try:
            # Decode bytes to string
            content = file_content.decode('utf-8')
            csv_file = io.StringIO(content)
            reader = csv.DictReader(csv_file)
            
            for row_num, row in enumerate(reader, start=2):  # Start from 2 (1 is header)
                results['total_rows'] += 1
                
                try:
                    # Clean and validate email
                    email = row.get('email', '').strip().lower()
                    if not email:
                        results['errors'] += 1
                        results['error_details'].append(f"Row {row_num}: Missing email")
                        continue
                    
                    # Validate email format
                    try:
                        validate_email(email)
                    except EmailNotValidError:
                        results['errors'] += 1
                        results['error_details'].append(f"Row {row_num}: Invalid email '{email}'")
                        continue
                    
                    # Check if already exists
                    existing = self.db.table('hackathon_participants')\
                        .select('id')\
                        .eq('email', email)\
                        .execute()
                    
                    if existing.data:
                        results['duplicates'] += 1
                        continue
                    
                    # Prepare data
                    participant_data = {
                        'name': row.get('name', '').strip() or email.split('@')[0],
                        'email': email,
                        'college': row.get('college', '').strip() or None,
                        'phone': row.get('phone', '').strip() or None
                    }
                    
                    # Insert into database
                    self.db.table('hackathon_participants').insert(participant_data).execute()
                    results['imported'] += 1
                    
                except Exception as e:
                    results['errors'] += 1
                    results['error_details'].append(f"Row {row_num}: {str(e)}")
            
        except Exception as e:
            results['errors'] += 1
            results['error_details'].append(f"CSV parsing error: {str(e)}")
        
        return results
    
    def get_all_participants(self) -> List[Dict]:
        """Get all hackathon participants"""
        result = self.db.table('hackathon_participants')\
            .select('*')\
            .order('imported_at', desc=True)\
            .execute()
        
        return result.data
    
    def check_participant_exists(self, email: str) -> bool:
        """Check if email exists in hackathon participants"""
        result = self.db.table('hackathon_participants')\
            .select('id')\
            .eq('email', email.strip().lower())\
            .execute()
        
        return len(result.data) > 0
    
    def get_participant_by_email(self, email: str) -> Dict:
        """Get hackathon participant by email"""
        result = self.db.table('hackathon_participants')\
            .select('*')\
            .eq('email', email.strip().lower())\
            .single()\
            .execute()
        
        return result.data
    
    def delete_all_participants(self) -> int:
        """Delete all hackathon participants (for re-import)"""
        result = self.db.table('hackathon_participants')\
            .delete()\
            .neq('id', 0)\
            .execute()
        
        return len(result.data) if result.data else 0