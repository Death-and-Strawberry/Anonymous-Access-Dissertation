from fastapi import APIRouter, HTTPException
from ..tor_client import tor_client

router = APIRouter()

@router.get("/status")
async def get_status():
    """Get service status"""
    return {
        "status": "running",
        "service": "Tor Hidden Service API",
        "message": "Service is running on Tor network"
    }

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@router.post("/tor/circuit")
async def create_new_circuit():
    """Create a new Tor circuit"""
    success = await tor_client.new_circuit()
    if success:
        return {"message": "New Tor circuit created successfully!"}
    else:
        raise HTTPException(status_code=500, detail="Failed to create new circuit")

@router.get("/tor/ip")
async def check_ip():
    """Check current IP through Tor"""
    try:
        ip = await tor_client.check_ip()
        return {"ip": ip, "message": "IP checked through Tor"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking IP: {str(e)}")