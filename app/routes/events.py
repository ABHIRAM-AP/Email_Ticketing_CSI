from fastapi import APIRouter, HTTPException, status
from app.models.event import EventCreate, EventResponse
from app.db import get_supabase
from typing import List

router = APIRouter(prefix="/events", tags=["Events"])


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_event(event: EventCreate):
    """Create a new event"""
    db = get_supabase()
    
    event_data = {
        'name': event.name,
        'description': event.description,
        'event_type': event.event_type.value,
        'event_date': event.event_date.isoformat(),
        'capacity': event.capacity,
        'registration_open': event.registration_open
    }
    
    try:
        result = db.table('events').insert(event_data).execute()
        return {"message": "Event created successfully", "event": result.data[0]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[dict])
async def get_all_events():
    """Get all events"""
    db = get_supabase()
    
    try:
        result = db.table('events').select('*').order('event_date', desc=False).execute()
        return result.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{event_id}", response_model=dict)
async def get_event(event_id: int):
    """Get event by ID"""
    db = get_supabase()
    
    try:
        result = db.table('events').select('*').eq('id', event_id).single().execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Event not found")
        
        # Get registration count
        count_result = db.table('registrations')\
            .select('id', count='exact')\
            .eq('event_id', event_id)\
            .execute()
        
        event_data = result.data
        event_data['registered_count'] = count_result.count
        
        return event_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{event_id}/toggle-registration", response_model=dict)
async def toggle_registration(event_id: int):
    """Toggle registration open/closed for an event"""
    db = get_supabase()
    
    try:
        # Get current state
        event = db.table('events').select('registration_open').eq('id', event_id).single().execute()
        
        if not event.data:
            raise HTTPException(status_code=404, detail="Event not found")
        
        new_state = not event.data['registration_open']
        
        # Update
        result = db.table('events')\
            .update({'registration_open': new_state})\
            .eq('id', event_id)\
            .execute()
        
        return {
            "message": f"Registration {'opened' if new_state else 'closed'}",
            "registration_open": new_state
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))