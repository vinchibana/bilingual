from pydantic import BaseModel
from typing import Optional
from enum import Enum

class TranslationStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class TranslationRequest(BaseModel):
    book_id: str
    target_language: str = "zh-hans"
    openai_key: str
    model: str = "chatgptapi"
    test: bool = False

class TranslationResponse(BaseModel):
    book_id: str
    status: TranslationStatus
    message: Optional[str] = None 
