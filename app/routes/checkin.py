from fastapi import APIRouter, HTTPException, status, Query
from app.services.checkin_service import CheckInService
from typing import Optional

router = APIRouter(prefix="/checkin", tags=["Check-in"])


@router.post("/qr", response_model=dict)
async def checkin_by_qr(ticket_id: str, event_id: int):
    """
    Check-in participant using QR code (ticket ID)
    
    Args:
        ticket_id: The ticket ID from QR code
        event_id: The event ID for this check-in
    """
    service = CheckInService()
    
    try:
        result = service.check_in_by_qr(ticket_id, event_id)
        
        if not result['success']:
            raise HTTPException(
                status_code=400,
                detail=result
            )
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Check-in failed: {str(e)}"
        )


@router.post("/email", response_model=dict)
async def checkin_by_email(email: str, event_id: int):
    """
    Check-in participant using email lookup (for hackathon participants)
    
    Args:
        email: Participant's email
        event_id: The event ID for this check-in
    """
    service = CheckInService()
    
    try:
        result = service.check_in_by_email(email, event_id)
        
        if not result['success']:
            raise HTTPException(
                status_code=400,
                detail=result
            )
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Check-in failed: {str(e)}"
        )


@router.get("/stats/{event_id}", response_model=dict)
async def get_checkin_stats(event_id: int):
    """
    Get check-in statistics for an event
    
    Returns:
        - Total registrations
        - Checked-in count
        - CSV check-ins
        - Remaining capacity
    """
    service = CheckInService()
    
    try:
        stats = service.get_event_checkin_stats(event_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/recent/{event_id}", response_model=list)
async def get_recent_checkins(event_id: int, limit: int = Query(default=10, le=50)):
    """
    Get recent check-ins for an event
    
    Args:
        event_id: Event ID
        limit: Maximum number of check-ins to return (default 10, max 50)
    """
    service = CheckInService()
    
    try:
        checkins = service.get_recent_checkins(event_id, limit)
        return checkins
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))