import datetime
from datetime import timedelta

from sqlalchemy.sql.functions import current_user
from typing import List
from app import schemas, models, functions,oauth2
from fastapi import FastAPI, Response, status, HTTPException, Depends,APIRouter, Query
from sqlalchemy.orm import Session
from app.database import get_db



router = APIRouter(
    prefix="/items/inventory",
    tags=["items_inventory"]
)


@router.get("/")
def get_items_inventory(db: Session = Depends(get_db),
                    current_user = Depends(oauth2.get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    items_inventory = db.query(models.Item).all()
    if items_inventory is None:
        raise HTTPException(status_code=404, detail="items not found.")

    return  items_inventory



@router.post("/", status_code=status.HTTP_201_CREATED)
def create_item_inven(item_invent: schemas.ItemInventory,
                      db: Session = Depends(get_db),
                      current_user = Depends(oauth2.get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    new_item_inven = models.Item(**item_invent.model_dump(by_alias=True))


    db.add(new_item_inven)
    db.commit()
    db.refresh(new_item_inven)

    return  new_item_inven
@router.get("/search/lowstock", response_model=List[schemas.ItemInventoryLowStockResponse])
def get_item_inventory_low_stock(
    filter: int = Query(10, gt=0),
    db: Session = Depends(get_db),
    current_user = Depends(oauth2.get_current_user)
):
    if not current_user.is_admin():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    low_stock_items = db.query(models.Item).filter(models.Item.item_quantity <= filter).all()

    if low_stock_items is None:
        raise HTTPException(status_code=404, detail="Item not found")

    return [schemas.ItemInventoryLowStockResponse.model_validate(item) for item in low_stock_items]


@router.get("/search", response_model=schemas.ItemInventoryResponse)
def search_inventory_by_id(query: int = None, db: Session = Depends(get_db),
                     current_user = Depends(oauth2.get_current_user)):


    item = db.query(models.Item).filter(models.Item.item_id == query).first()


    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    return item





@router.get("/{id}",response_model=schemas.ItemInventoryResponse)
def get_item_inventory(id: int,
                       db: Session = Depends(get_db),
                       current_user: int = Depends(oauth2.get_current_user)):

    item_inven = db.query(models.Item).filter(models.Item.item_id == id).first()

    if item_inven is None:
        raise HTTPException(status_code=404, detail="Item not found")

    return  item_inven



@router.put("/name/up{id}")
def update_item_inventory_name(id: int,
                               item_invent: schemas.UpdateItemInventoryName,
                               db: Session = Depends(get_db),
                               current_user = Depends(oauth2.get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    if db.query(models.Item).filter(models.Item.item_id == id).first() is None:
        raise HTTPException(status_code=404,
                            detail=f"Item with id:{id} not found")

    week_start_date = datetime.date.today() - timedelta(days=datetime.date.today().weekday())

    functions.update_itemsold_name(db, id, item_invent.model_dump(by_alias=True))    #Updates the name across all the item tables
    functions.update_dailysales_name(db, id, item_invent.model_dump(by_alias=True))
    functions.update_weeklysales_name(db, id, item_invent.model_dump(by_alias=True))
    functions.update_monthlysales_name(db, id, item_invent.model_dump(by_alias=True))
    functions.update_yearly_sales_name(db, id, item_invent.model_dump(by_alias=True))
    return functions.update_item_by_id(db, id, item_invent.model_dump(by_alias=True))


@router.put("/quantity/up{id}")
def update_item_inventory_quantity(id: int,
                                   item_invent: schemas.UpdateItemInventoryQuantity,
                                   db: Session = Depends(get_db),
                                   current_user = Depends(oauth2.get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    return functions.update_item_by_id(db, id, item_invent.model_dump(by_alias=True))


@router.put("/price/up{id}")
def update_item_inventory_price(id: float,
                                item_invent: schemas.UpdateItemInventoryPrice,
                                db: Session = Depends(get_db),
                                current_user = Depends(oauth2.get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    return functions.update_item_by_id(db, id, item_invent.model_dump(by_alias=True))

@router.put("/up{id}")
def update_item_inventory(id: int,
                          item_invent: schemas.UpdateItemInventory,
                          db: Session = Depends(get_db),
                          current_user = Depends(oauth2.get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")


    return functions.update_item_by_id(db, id, item_invent.model_dump(by_alias=True))


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item_inventory(id: int,
                          db: Session = Depends(get_db),
                          current_user = Depends(oauth2.get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    deleted_item = db.query(models.Item).filter(models.Item.item_id == id)
    if deleted_item.first() is None:
        raise HTTPException(status_code=404, detail="Item not found")

    deleted_item.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
