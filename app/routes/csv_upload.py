from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.services.csv_service import CSVService
from app.models.checkin import CSVUploadResponse
from typing import List

router = APIRouter(prefix="/csv", tags=["CSV Upload"])


@router.post("/upload", response_model=dict)
async def upload_hackathon_csv(file: UploadFile = File(...)):
    """
    Upload CSV file with hackathon participants
    
    Expected CSV format:
    - Headers: name, email, college, phone
    - Minimum required: email
    """
    
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are allowed"
        )
    
    try:
        # Read file content
        content = await file.read()
        
        # Parse and import
        service = CSVService()
        results = service.parse_csv(content)
        
        return {
            "message": "CSV processed successfully",
            "total_rows": results['total_rows'],
            "imported": results['imported'],
            "duplicates": results['duplicates'],
            "errors": results['errors'],
            "error_details": results['error_details'][:10]  # Limit error details
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing CSV: {str(e)}"
        )


@router.get("/participants", response_model=List[dict])
async def get_all_participants():
    """Get all imported hackathon participants"""
    service = CSVService()
    
    try:
        participants = service.get_all_participants()
        return participants
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/participants/{email}")
async def get_participant_by_email(email: str):
    """Check if email exists in hackathon participants"""
    service = CSVService()
    
    try:
        exists = service.check_participant_exists(email)
        
        if not exists:
            return {
                "exists": False,
                "message": "Email not found in hackathon participants"
            }
        
        participant = service.get_participant_by_email(email)
        return {
            "exists": True,
            "participant": participant
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/participants", response_model=dict)
async def delete_all_participants():
    """Delete all hackathon participants (use with caution!)"""
    service = CSVService()
    
    try:
        deleted_count = service.delete_all_participants()
        return {
            "message": f"Deleted {deleted_count} participants",
            "deleted_count": deleted_count
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/stats", response_model=dict)
async def get_csv_stats():
    """Get statistics about imported hackathon participants"""
    service = CSVService()
    
    try:
        participants = service.get_all_participants()
        
        return {
            "total_participants": len(participants),
            "latest_import": participants[0]['imported_at'] if participants else None
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))