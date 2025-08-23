from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from ..utils import render_template
from ..database import get_db
from ..crud import get_user_by_pseudo_id

router = APIRouter()

def get_current_user_id(request):
    return request.cookies.get("user")

def get_current_user(request: Request, db: Session) -> dict:
    """Get current user from database"""
    pseudo_id = get_current_user_id(request)
    if not pseudo_id:
        return None
    
    user = get_user_by_pseudo_id(db, pseudo_id)
    if not user:
        return None
    
    return {
        "pseudo_id": user.pseudo_id,
        "created_at": user.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        "last_seen": user.last_seen.strftime("%Y-%m-%d %H:%M:%S"),
        "has_credentials": user.bbs_public_key is not None,
        "merkle_root": user.merkle_root[:16] + "..." if user.merkle_root else "None"
    }

@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    if not get_current_user_id(request):
        return RedirectResponse(url="/auth/login")
    
    user_info = get_current_user(request, db)
    if not user_info:
        # If User cookie exists but user not found in DB
        response = RedirectResponse(url="/auth/login")
        response.delete_cookie("user", path="/")
        return response
    
    return render_template("dashboard.html", **user_info)