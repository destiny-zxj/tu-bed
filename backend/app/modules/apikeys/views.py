from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.core.database import get_db
from app.core.security import generate_api_key, get_current_user
from app.modules.apikeys.items import ApiKeyCreateItem
from app.modules.apikeys.models import ApiKey, ApiKeyCreated, ApiKeyPublic
from app.modules.auth.models import User

router = APIRouter(prefix="/api/apikeys", tags=["apikeys"])


@router.get("", response_model=list[ApiKeyPublic])
def list_api_keys(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(ApiKey).filter(ApiKey.owner_id == current_user.id).all()


@router.post("", response_model=ApiKeyCreated)
def create_api_key(
    item: ApiKeyCreateItem,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    raw, key_hash, prefix = generate_api_key()
    record = ApiKey(owner_id=current_user.id, name=item.name, key_hash=key_hash, prefix=prefix)
    db.add(record)
    db.commit()
    db.refresh(record)
    return ApiKeyCreated(**{**ApiKeyPublic.model_validate(record).model_dump(), "key": raw})


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_api_key(
    key_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    record = db.query(ApiKey).filter(ApiKey.id == key_id, ApiKey.owner_id == current_user.id).first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API Key 不存在")
    db.delete(record)
    db.commit()
