from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_logger


router = APIRouter(prefix="/general", tags=["general"])

@router.get("/health")
def health(logger=Depends(get_logger)):
    logger.info("health_check")
    return {"status": "ok"}

@router.get("/ready")
def ready(db: Session = Depends(get_db), logger=Depends(get_logger)):
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        logger.exception("db_not_ready")
        raise HTTPException(status_code=503, detail="Database not ready")
    return {"status": "ok", "db": "ok"}
