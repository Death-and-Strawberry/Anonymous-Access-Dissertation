from sqlalchemy.orm import Session
from .models import PseudoUser
import hashlib

def generate_pseudo_id(pk_bind_key: bytes) -> str:
    """Generate a deterministic pseudo ID from the public binding key"""
    hash_obj = hashlib.sha256(pk_bind_key)
    return hash_obj.hexdigest()[:16]  # first 16 chars for readability

def get_user_by_pk_bind(db: Session, pk_bind_key: bytes) -> PseudoUser:
    """Get user by their public binding key"""
    return db.query(PseudoUser).filter(PseudoUser.pk_bind_key == pk_bind_key).first()

def get_user_by_pseudo_id(db: Session, pseudo_id: str) -> PseudoUser:
    """Get user by pseudo ID"""
    return db.query(PseudoUser).filter(PseudoUser.pseudo_id == pseudo_id).first()

def create_user(db: Session, pk_bind_key: bytes, bbs_public_key: bytes = None, 
                merkle_root: str = None) -> PseudoUser:
    """Create a new pseudo user"""
    pseudo_id = generate_pseudo_id(pk_bind_key)
    
    user = PseudoUser(
        pseudo_id=pseudo_id,
        pk_bind_key=pk_bind_key,
        bbs_public_key=bbs_public_key,
        merkle_root=merkle_root
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def update_user_credentials(db: Session, user: PseudoUser, 
                            bbs_public_key: bytes, merkle_root: str) -> PseudoUser:
    """Update user's credential information"""
    user.bbs_public_key = bbs_public_key
    user.merkle_root = merkle_root
    user.update_last_seen()
    
    db.commit()
    db.refresh(user)
    return user
