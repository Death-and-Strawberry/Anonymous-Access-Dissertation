from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Tuple
import base64, json

from ..zkp import (
    load_merkle_root, load_vk_json_bytes,
    verify_bbs_selective_disclosure, verify_plonk_with_snarkjs, derive_pseudo_user_id
)

router = APIRouter(tags=["verification"])

class RevealedPair(BaseModel):
    name: str
    value: str                 # base64 for binary, utf8 for plain numbers/strings
    encoding: str = "utf8"     # "utf8" | "base64"

class VerifyPayload(BaseModel):
    # BBS+ proof
    bbs_public_key_b64: str    
    bbs_proof: str             
    bbs_nonce: str             
    message_count: int         

    # Revealed in the same order the signing was done
    revealed: List[RevealedPair]

    # PLONK proof 
    plonk_proof: str           # base64 of proof.json
    plonk_public: str          # base64 of public.json

    # For freshness / revocation 
    merkle_root_hex: str
    epoch: int

@router.post("/verify")
async def verify(payload: VerifyPayload):
    # freshness check against server-published root (still in progress, not 100% sure what to do)
    current = load_merkle_root()
    if current is not None:
        root_now, epoch_now = current
        if payload.epoch != epoch_now or payload.merkle_root_hex.lower() != root_now:
            raise HTTPException(400, "Outdated root/epoch. Regenerate proof against the current root.")

    # Decode revealed fields (should be the same order) which is: expiry_year, expiry_month, pk_bind, commitment
    revealed_ordered: List[Tuple[str, bytes]] = []
    pk_bind_bytes = None
    commitment_bytes = None

    for item in payload.revealed:
        if item.encoding == "base64":
            b = base64.b64decode(item.value)
        elif item.encoding == "utf8":
            b = item.value.encode()
        else:
            raise HTTPException(400, f"Unknown encoding for {item.name}")
        revealed_ordered.append((item.name, b))
        if item.name == "pk_bind":
            pk_bind_bytes = b
        if item.name == "commitment":
            commitment_bytes = b

    if pk_bind_bytes is None or commitment_bytes is None:
        raise HTTPException(400, "Revealed set must include pk_bind and commitment.")

    # Verify BBS+ selective disclosure
    bbs_public_key = base64.b64decode(payload.bbs_public_key_b64)

    ok_bbs = verify_bbs_selective_disclosure(
        proof_b64=payload.bbs_proof,
        nonce_b64=payload.bbs_nonce,
        message_count=payload.message_count,
        revealed_ordered=revealed_ordered,
        bbs_public_key_bytes=bbs_public_key
    )
    if not ok_bbs:
        raise HTTPException(401, "BBS+ proof invalid")

    # Verify PLONK proof
    vk_bytes = load_vk_json_bytes()
    ok_plonk = verify_plonk_with_snarkjs(
        vk_json_bytes=vk_bytes,
        proof_json_b64=payload.plonk_proof,
        public_json_b64=payload.plonk_public
    )
    if not ok_plonk:
        raise HTTPException(401, "ZK (PLONK) proof invalid")

    # Pseudonymous identity from pk_bind (stable across reuse of the same binding key)
    user_id = derive_pseudo_user_id(pk_bind_bytes)


