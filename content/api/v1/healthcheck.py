"""Хелсчек."""
from fastapi import APIRouter

router = APIRouter()


@router.get("")
def health_check():
    """Хелсчек."""
    return {"status": "healthy"}
