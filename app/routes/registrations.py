from fastapi import APIRouter, HTTPException, status
from app.models.registration import RegistrationCreate, RegistrationResponse
from app.services.registration_service import RegistrationService
from typing import List

router = APIRouter(prefix="/registrations", tags=["Registrations"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def register_for_event(registration: RegistrationCreate):
    """
    Register a participant for an event
    Generates ticket and sends email
    """
    service = RegistrationService()
    
    try:
        result = await service.create_registration(registration)
        
        return {
            "message": "Registration successful! Check your email for the ticket.",
            "registration_id": result['registration_id'],
            "ticket_id": result['ticket_id'],
            "email_sent": result['email_sent']
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")


@router.get("/event/{event_id}", response_model=List[dict])
async def get_event_registrations(event_id: int):
    """Get all registrations for a specific event"""
    service = RegistrationService()
    
    try:
        registrations = service.get_registrations_by_event(event_id)
        return registrations
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/ticket/{ticket_id}", response_model=dict)
async def get_registration_by_ticket(ticket_id: str):
    """Get registration details by ticket ID"""
    service = RegistrationService()
    
    try:
        registration = service.get_registration_by_ticket(ticket_id)
        
        if not registration:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        return registration
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/verify/{ticket_id}", response_model=dict)
async def verify_ticket(ticket_id: str):
    """
    Verify if a ticket is valid
    Used for quick validation without full details
    """
    service = RegistrationService()
    
    try:
        registration = service.get_registration_by_ticket(ticket_id)
        
        if not registration:
            return {"valid": False, "message": "Invalid ticket"}
        
        if registration['checked_in']:
            return {
                "valid": True,
                "already_checked_in": True,
                "message": "Ticket already used",
                "checked_in_at": registration['checked_in_at']
            }
        
        return {
            "valid": True,
            "already_checked_in": False,
            "participant_name": registration['name'],
            "event_name": registration['events']['name']
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))