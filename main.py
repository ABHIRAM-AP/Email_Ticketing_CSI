from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from app.routes import events, registrations, csv_upload, checkin
from app.config import settings
import os

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Event ticketing system with QR code generation and email delivery",
    version="2.0.0 - Phase 2"
)

# CORS middleware (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(events.router)
app.include_router(registrations.router)
app.include_router(csv_upload.router)
app.include_router(checkin.router)


@app.get("/")
async def root():
    return {
        "message": "Event Ticketing System API - Phase 2",
        "version": "2.0.0",
        "status": "running",
        "features": [
            "Event Management",
            "Registration & Ticketing",
            "CSV Import (Hackathon Participants)",
            "Check-in System (QR & Email)"
        ]
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Admin Dashboard"""
    with open("templates/dashboard.html" , "r",encoding='utf-8') as f:
        return f.read()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)