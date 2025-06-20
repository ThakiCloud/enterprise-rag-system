from pydantic import BaseModel
from typing import Optional, Dict, Any

class DocumentUploadResponse(BaseModel):
    message: str
    document_id: str
    filename: str
    status: str
    metadata: Optional[Dict[str, Any]] = None 