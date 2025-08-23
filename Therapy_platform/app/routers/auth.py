from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Annotated, Optional
from sqlalchemy.orm import Session
from ..utils import render_template
from ..bbs_verify import verify_bbs_proof
from ..database import get_db
from ..crud import get_user_by_pk_bind, create_user, update_user_credentials, generate_pseudo_id
from ..models import PseudoUser, AuthChallenge
import base64
import os
import hashlib
from datetime import datetime, timedelta
import uuid
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

router = APIRouter()

# Type aliases for Pydantic
Base64Str = Annotated[str, Field(pattern="^[A-Za-z0-9+/=]+$")]
HexStr = Annotated[str, Field(pattern="^[0-9a-fA-F]+$")]

# Payload models
class ProofPayload(BaseModel):
    bbs_public_key_b64: Base64Str
    bbs_proof: Base64Str
    bbs_nonce: Base64Str
    message_count: int
    revealed: list 
    plonk_proof: Base64Str
    plonk_public: Base64Str
    merkle_root_hex: HexStr
    epoch: int
    # Authentication via challenge-response
    challenge_id: str
    challenge_signature: Base64Str

class ChallengeRequest(BaseModel):
    pk_bind_key: Base64Str

# Detect local dev for cookie
DEV = os.environ.get("DEV", "1") == "1"

def create_challenge(db: Session, pk_bind_key: bytes) -> dict:
    """Create a new authentication challenge"""
    challenge_id = str(uuid.uuid4())
    challenge_bytes = os.urandom(32)  # Random 32-byte challenge
    expires_at = datetime.now() + timedelta(minutes=10)  # Challenge expires in 10 minutes
    
    challenge = AuthChallenge(
        challenge_id=challenge_id,
        challenge_bytes=challenge_bytes,
        pk_bind_key=pk_bind_key,
        expires_at=expires_at
    )
    
    db.add(challenge)
    db.commit()
    
    return {
        "challenge_id": challenge_id,
        "challenge": base64.b64encode(challenge_bytes).decode(),
        "expires_at": expires_at.isoformat()
    }

def verify_challenge_signature(db: Session, challenge_id: str, signature: bytes, pk_bind_key: bytes) -> bool:
    """Verify that the challenge was signed correctly"""
    # Get the challenge from database
    challenge = db.query(AuthChallenge).filter(
        AuthChallenge.challenge_id == challenge_id,
        AuthChallenge.pk_bind_key == pk_bind_key,
        AuthChallenge.used == "false"
    ).first()
    
    if not challenge:
        return False
    
    # Check if challenge expired
    if datetime.now() > challenge.expires_at:
        return False
    
    try:
        # Verify the signature using Nacl
        verify_key = VerifyKey(pk_bind_key)
        verify_key.verify(challenge.challenge_bytes, signature)
        
        # Mark challenge as used
        challenge.used = "true"
        db.commit()
        
        return True
    except (BadSignatureError, Exception):
        return False

def extract_binding_keys(revealed: list):
    """Extract pk_bind from revealed attributes"""
    for item in revealed:
        if item["name"] == "pk_bind":
            if item["encoding"] == "base64":
                return base64.b64decode(item["value"])
            else:
                return item["value"].encode()
    raise ValueError("pk_bind not found in revealed attributes")

# GET the /auth/challenge 
@router.post("/challenge")
async def get_challenge(request: ChallengeRequest, db: Session = Depends(get_db)):
    """Create an authentication challenge for the user to sign"""
    try:
        pk_bind_key = base64.b64decode(request.pk_bind_key)
        challenge_data = create_challenge(db, pk_bind_key)
        return JSONResponse(challenge_data)
    except Exception as e:
        return JSONResponse({"error": f"Challenge creation failed: {str(e)}"}, status_code=400)

# GET /auth/login → serves login page
@router.get("/login")
async def login_page():
    return render_template("login.html")

# POST /auth/login → handles JSON payload with challenge response
@router.post("/login")
async def login(payload: ProofPayload, db: Session = Depends(get_db)):
    try:
        # Decode base64 fields
        bbs_pub = base64.b64decode(payload.bbs_public_key_b64)
        bbs_proof = base64.b64decode(payload.bbs_proof)
        nonce = base64.b64decode(payload.bbs_nonce)
        challenge_signature = base64.b64decode(payload.challenge_signature)

        # Prepare revealed attributes
        revealed = {}
        for r in payload.revealed:
            if r["encoding"] == "base64":
                revealed[r["name"]] = base64.b64decode(r["value"])
            else:
                revealed[r["name"]] = r["value"].encode()

        # Extract binding key for user identification
        pk_bind_key = extract_binding_keys(payload.revealed)

        # Verify challenge signature first
        if not verify_challenge_signature(db, payload.challenge_id, challenge_signature, pk_bind_key):
            return JSONResponse({"error": "Invalid or expired challenge signature"}, status_code=401)

        # Verify BBS proof
        verified = verify_bbs_proof(bbs_proof, revealed, bbs_pub, nonce, payload.message_count)
        
    except Exception as e:
        return JSONResponse({"error": f"Verification failed: {str(e)}"}, status_code=400)

    if not verified:
        return JSONResponse({"error": "Invalid proof"}, status_code=401)

    try:
        # Check if user exists
        user = get_user_by_pk_bind(db, pk_bind_key)
        
        if user is None:
            # Create a new pseudo user with minimal info
            user = create_user(
                db=db,
                pk_bind_key=pk_bind_key,
                bbs_public_key=bbs_pub,
                merkle_root=payload.merkle_root_hex
            )
        else:
            # Update existing user's credentials
            user = update_user_credentials(
                db=db,
                user=user,
                bbs_public_key=bbs_pub,
                merkle_root=payload.merkle_root_hex
            )

        # Set pseudo-identity cookie
        response = JSONResponse({"success": True, "pseudo_id": user.pseudo_id})
        response.set_cookie(
            key="user",
            value=user.pseudo_id,
            httponly=True,
            secure=False if DEV else True,
            samesite="lax" if DEV else "strict",
            path="/"
        )
        
        return response
        
    except Exception as e:
        return JSONResponse({"error": f"Database error: {str(e)}"}, status_code=500)


# Optional logout
@router.get("/logout")
async def logout():
    response = JSONResponse({"success": True})
    response.delete_cookie("user", path="/")
    return response
