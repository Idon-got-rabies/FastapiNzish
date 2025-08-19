import datetime
import string
from datetime import timedelta

from dns.resolver import query
from mako.util import restore__ast
from sqlalchemy import func, String
from sqlalchemy.sql.functions import current_user
from typing import List
from app import schemas, models, functions,oauth2
from fastapi import FastAPI, Response, status, HTTPException, Depends,APIRouter, Query
from sqlalchemy.orm import Session
from app.database import get_db
from sqlalchemy import or_
from starlette.concurrency import run_in_threadpool



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

@router.get("/total/stock/")
async def get_total_stock(db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    def sync_db():
        total_stock = db.query(models.Item).filter(models.Item.item_quantity > 0).count()
        net_worth = db.query(func.sum(models.Item.item_price * models.Item.item_quantity)).scalar() or 0
        if total_stock and net_worth is None:
            raise HTTPException(status_code=404, detail="items not found.")
        return {
            "total_stock": total_stock,
            "net_worth": net_worth
        }
    return await run_in_threadpool(sync_db)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_item_inven(item_invent: schemas.ItemInventory,
                      db: Session = Depends(get_db),
                      current_user = Depends(oauth2.get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")


    def sync_db():
        new_item_inven = models.Item(**item_invent.model_dump(by_alias=True))
        new_item_inven.item_id = functions.assign_random_id(db, 1000, 9999)


        db.add(new_item_inven)
        db.commit()
        db.refresh(new_item_inven)
        return new_item_inven

    return await run_in_threadpool(sync_db)
@router.get("/search/lowstock", response_model=List[schemas.ItemInventoryLowStockResponse])
async def get_item_inventory_low_stock(
    filter_quantity: int = Query(10, gt=-1),
    db: Session = Depends(get_db),
    current_user = Depends(oauth2.get_current_user)
):

    def sync_db():

        if not current_user.is_admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

        low_stock_items = db.query(models.Item).filter(models.Item.item_quantity <= filter_quantity).all()


        return[
    schemas.ItemInventoryLowStockResponse(
        item_name=item.item_name,
        item_id=item.item_id,
        item_quantity=item.item_quantity
    )for item in low_stock_items]


    try:
        return await run_in_threadpool(sync_db)
    except Exception as e:
        print(f"ERROR: {e}")
        raise HTTPException(status_code=500, detail="Server error")
@router.get("/search", response_model=list[schemas.ItemInvenSarhResp])
async def search_inventory_by_id(query: str| int| None = Query(default=None, description="search"), db: Session = Depends(get_db),
                     current_user = Depends(oauth2.get_current_user)):

    def sync_db():
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )

        if not query:
            raise HTTPException(status_code=404, detail="Item not found.")

        results = []

        # Try numeric search
        try:
            query_int = int(query)
            item = db.query(models.Item).filter(models.Item.item_id == query_int).first()
            if item:
                results.append(item)
        except ValueError:
            pass  # query was not a number, continue with name search

        # Search by name or partial ID string
        items = db.query(models.Item).filter(
            or_(
                models.Item.item_name.ilike(f"%{query}%"),
                models.Item.item_id.cast(String).ilike(f"%{query}%")
            )
        ).distinct.all()

        if items:
            results.extend(items)

        if not results:
            raise HTTPException(status_code=404, detail="Item not found.")
        unique_results = {item.item_id: item for item in results}.values()

        if not unique_results:
            raise HTTPException(status_code=404, detail="Item not found.")

        return list(unique_results)

    return await run_in_threadpool(sync_db)




@router.get("/{id}",response_model=schemas.ItemInventoryResponse)
async def get_item_inventory(id: int,
                       db: Session = Depends(get_db),
                       current_user: int = Depends(oauth2.get_current_user)):

    def sync_db():
        return db.query(models.Item).filter(models.Item.item_id == id).first()

    item_inven = await run_in_threadpool(sync_db)

    if item_inven is None:
        raise HTTPException(status_code=404,  detail="Item not found")

    return  item_inven



@router.put("/name/up{id}")
async def update_item_inventory_name(id: int,
                               item_invent: schemas.UpdateItemInventoryName,
                               db: Session = Depends(get_db),
                               current_user = Depends(oauth2.get_current_user)):
    def sync_db():
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


    return await run_in_threadpool(sync_db)



@router.put("/quantity/up{id}")
async def update_item_inventory_quantity(id: int,
                                   item_invent: schemas.UpdateItemInventoryQuantity,
                                   db: Session = Depends(get_db),
                                   current_user = Depends(oauth2.get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    def sync_db():
        db_quantity = db.query(models.Item).filter(models.Item.item_id == id).first()
        if db_quantity is None:
            raise HTTPException(status_code=404, detail=f"No item with id {id} was found")

        quantity = db_quantity.item_quantity + item_invent.itemInven_quantity
        update_data = item_invent.model_dump(by_alias=True)
        update_data["item_quantity"] = quantity


        return functions.update_item_by_id(db, id, update_data)
    return await run_in_threadpool(sync_db)


@router.put("/price/up{id}")
async def update_item_inventory_price(id: float,
                                item_invent: schemas.UpdateItemInventoryPrice,
                                db: Session = Depends(get_db),
                                current_user = Depends(oauth2.get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    def sync_db():
        return functions.update_item_by_id(db, id, item_invent.model_dump(by_alias=True))
    return await run_in_threadpool(sync_db)

@router.put("/up{id}")
async def update_item_inventory(id: int,
                          item_invent: schemas.UpdateItemInventory,
                          db: Session = Depends(get_db),
                          current_user = Depends(oauth2.get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    def sync_db():
        return functions.update_item_by_id(db, id, item_invent.model_dump(by_alias=True))
    return await run_in_threadpool(sync_db)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item_inventory(id: int,
                          db: Session = Depends(get_db),
                          current_user = Depends(oauth2.get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    def sync_db():
        deleted_item = db.query(models.Item).filter(models.Item.item_id == id)
        if deleted_item.first() is None:
            raise HTTPException(status_code=404, detail="Item not found")

        deleted_item.delete(synchronize_session=False)
        db.commit()

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return await run_in_threadpool(sync_db)
