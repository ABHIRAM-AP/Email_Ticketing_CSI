from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import events, registrations
from app.config import settings

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Event ticketing system with QR code generation and email delivery",
    version="1.0.0"
)

# CORS middleware (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(events.router)
app.include_router(registrations.router)


@app.get("/")
async def root():
    return {
        "message": "Event Ticketing System API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)