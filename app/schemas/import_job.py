from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class ImportJobResponse(BaseModel):
    id: str
    status: str  # "pending", "completed", "failed"
    imported_count: Optional[int] = None
    discarded_count: Optional[int] = None
    discard_reasons: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None
