from sqlalchemy import Column, Integer, String, DateTime, LargeBinary
from datetime import datetime
from .database import Base

class PseudoUser(Base):
    __tablename__ = "pseudo_users"
    
    id = Column(Integer, primary_key=True, index=True)

    pseudo_id = Column(String, unique=True, index=True, nullable=False)
    pk_bind_key = Column(LargeBinary, unique=True, index=True, nullable=False)  # Public binding key
    bbs_public_key = Column(LargeBinary, nullable=True)  # Needed for BBS proof verification
    merkle_root = Column(String, nullable=True)          # Needed for BBS proof verification
    
    # Optional metadata
    created_at = Column(DateTime, default=datetime.now)
    last_seen = Column(DateTime, default=datetime.now)
    
    def update_last_seen(self):
        self.last_seen = datetime.now()

class AuthChallenge(Base):
    __tablename__ = "auth_challenges"
    
    id = Column(Integer, primary_key=True, index=True)
    challenge_id = Column(String, unique=True, index=True, nullable=False)
    challenge_bytes = Column(LargeBinary, nullable=False)
    pk_bind_key = Column(LargeBinary, nullable=False)  # Public key this challenge is for
    created_at = Column(DateTime, default=datetime.now)
    expires_at = Column(DateTime, nullable=False)
    used = Column(String, default="false")  # "false", "true"
