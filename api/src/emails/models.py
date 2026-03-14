from typing import List, Optional

from pydantic import BaseModel


# ---- Email Schema

class EmailSchema(BaseModel):
    subject: Optional[str] = None
    body: Optional[str] = None
    recipients: List[str]
    cc: Optional[List[str]] = None
    bcc: Optional[List[str]] = None
    managerName: Optional[str] = None
    managerEmail: Optional[str] = None
