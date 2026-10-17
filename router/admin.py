from fastapi import APIRouter, Depends,HTTPException
from fastapi.responses import JSONResponse
from database import SessionLocal
from sqlalchemy.orm import Session
from typing import Annotated
from pydantic import BaseModel
from router.auth import get_current_user
from models import Users, Products, Orders

router = APIRouter()

class add_product(BaseModel):
    img_url: str
    title : str
    description : str
    price : int
    total_available : int

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.post("/admin/add_product")
def add_product(db: db_dependency, user: user_dependency, new_product: add_product):
    if user is None or user.get('role') != "admin":
        raise HTTPException(status_code=403,detail="Failed Authentication")
    product_model = Products(
        **new_product.model_dump()
    )
    db.add(product_model)
    db.commit()
    return JSONResponse(status_code=201, content={'message':'Product Added Successfully'})

@router.get("/admin/all_order/{page}")
def all_order(db: db_dependency, user: user_dependency,page:int):
    if user is None or user.get('role') != "admin":
        raise HTTPException(status_code=401,detail="Failed Authentication")
    if page < 1:
        raise HTTPException(status_code=400,detail="Page must be greater than 0")
    limit = 10;
    skip = (page - 1) * limit
    orders = db.query(Orders).filter(Orders.is_completed == False)
    total_order = orders.count()

    orders = (orders.order_by(Orders.id.asc()).offset(skip).limit(limit).all())
    total_page = (total_order + limit - 1) // limit

    return{
        "page": page,
        "per_page": limit,
        "total_page" : total_page,
        "total_order" : total_order,
        "orders" : orders,
    }