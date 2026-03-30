from fastapi import APIRouter, HTTPException, status, Query
from app.services.checkin_service import CheckInService
from typing import Optional

router = APIRouter(prefix="/checkin", tags=["Check-in"])


@router.post("/qr", response_model=dict)
async def checkin_by_qr(ticket_id: str):
    """
    Check-in participant using QR code (ticket ID)
    
    Args:
        ticket_id: The ticket ID from QR code
    """
    service = CheckInService()
    
    try:
        result = service.check_in_by_qr(ticket_id)
        
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
async def checkin_by_email(email: str):
    """
    Check-in participant using email lookup (for hackathon participants)
    
    Args:
        email: Participant's email
    """
    service = CheckInService()
    
    try:
        result = service.check_in_by_email(email)
        
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


@router.get("/stats", response_model=dict)
async def get_checkin_stats():
    """
    Get check-in statistics for the hackathon
    
    Returns:
        - Total registrations
        - Checked-in count
        - CSV check-ins
        - Remaining capacity
    """
    service = CheckInService()
    
    try:
        stats = service.get_event_checkin_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/recent", response_model=list)
async def get_recent_checkins(limit: int = Query(default=10, le=50)):
    """
    Get recent check-ins for the hackathon
    
    Args:
        limit: Maximum number of check-ins to return (default 10, max 50)
    """
    service = CheckInService()
    
    try:
        checkins = service.get_recent_checkins(limit)
        return checkins
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))