from pydantic import BaseModel
from typing import Optional


class EasyLoginResponse(BaseModel):
    success: bool
    token: Optional[str] = None
    message: Optional[str] = None


class HardLoginResponse(BaseModel):
    success: bool
    token: Optional[str] = None
    message: Optional[str] = None
    redirect: Optional[str] = None
    ttl_seconds: Optional[int] = None


class ExtremeInitResponse(BaseModel):
    session_id: str
    ws_ticket: str


class ExtremePowChallenge(BaseModel):
    type: str
    prefix: str
    difficulty: Optional[int] = None


class ExtremePowResult(BaseModel):
    type: str
    intermediate_token: str


class ExtremeVerifyTokenResponse(BaseModel):
    token: Optional[str] = None
    encrypted_payload: Optional[str] = None


class ExtremeCompleteResponse(BaseModel):
    token: str
    proof_hash: str
    elapsed_ms: int


class ServiceResult(BaseModel):
    success: bool
    elapsed_ms: int
    token: Optional[str] = None
    message: Optional[str] = None
    proof_hash: Optional[str] = None
    error: Optional[str] = None
