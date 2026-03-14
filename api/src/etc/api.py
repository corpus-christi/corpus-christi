import os
from datetime import datetime

from fastapi import APIRouter

router = APIRouter()


@router.get("/ping")
def ping():
    """Basic smoke test that application server is running."""
    return {
        'ping': 'pong',
        'os': os.name,
        'cwd': os.getcwd(),
        'pid': os.getpid(),
        'now': datetime.now().isoformat(),
        'utc': datetime.utcnow().isoformat(),
    }
