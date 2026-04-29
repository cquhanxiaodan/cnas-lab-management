from typing import Type, List, Optional, Any, Dict
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.services.auth import get_current_user
from app.models.models import User


def create_crud_router(
    model: Type,
    create_schema: Type[BaseModel],
    update_schema: Type[BaseModel],
    response_schema: Type[BaseModel],
    prefix: str,
    tags: List[str],
    search_fields: Optional[List[str]] = None,
):
    router = APIRouter(prefix=prefix, tags=tags)

    @router.get("", response_model=List[response_schema])
    def list_items(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=500),
        search: Optional[str] = None,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        query = db.query(model)
        if search and search_fields:
            conditions = []
            for field in search_fields:
                conditions.append(getattr(model, field).icontains(search))
            from sqlalchemy import or_
            query = query.filter(or_(*conditions))
        return query.offset(skip).limit(limit).all()

    @router.get("/{item_id}", response_model=response_schema)
    def get_item(
        item_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        item = db.query(model).filter(model.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="记录不存在")
        return item

    @router.post("", response_model=response_schema, status_code=201)
    def create_item(
        data: create_schema,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        item = model(**data.model_dump(exclude_unset=True))
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    @router.put("/{item_id}", response_model=response_schema)
    def update_item(
        item_id: int,
        data: update_schema,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        item = db.query(model).filter(model.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="记录不存在")
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(item, key, value)
        db.commit()
        db.refresh(item)
        return item

    @router.delete("/{item_id}")
    def delete_item(
        item_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        item = db.query(model).filter(model.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="记录不存在")
        db.delete(item)
        db.commit()
        return {"message": "删除成功"}

    return router
