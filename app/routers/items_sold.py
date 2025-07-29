from app import schemas, models, functions,oauth2
from fastapi import FastAPI, Response, status, HTTPException, Depends,APIRouter
from sqlalchemy.orm import Session
from app.database import get_db
from typing import cast, Optional, Annotated, List
from sqlalchemy.exc import SQLAlchemyError
from datetime import date, time, datetime, timedelta, UTC, timezone
from sqlalchemy import and_, func
from fastapi.params import Query
from zoneinfo import ZoneInfo


from app.models import DailySales
from app.schemas import ItemSoldResponse

router = APIRouter(prefix="/items/sale",
                   tags=["items_sold"])

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.ItemSoldResponse)
def add_sold_item(item_info_user: schemas.ItemSold, db: Session = Depends(get_db),
                  current_user = Depends(oauth2.get_current_user)):


    item_db = db.query(models.Item).filter(models.Item.item_id == item_info_user.item_id).first()
    if item_db is None:
        raise HTTPException(status_code=404,
                            detail="Item is not registered in inventory")
    if item_info_user.item_quantity > item_db.item_quantity:
        raise HTTPException(status_code=400,
                            detail=f"Unable to complete. Item left in inventory is {item_db.item_quantity}")

    total_price = functions.calculate_total_price(db, item_info_user.item_id, item_info_user.item_quantity)

    item_name = cast(str, item_db.item_name)
    item_db.item_quantity -= item_info_user.item_quantity

    new_item = models.ItemSold(item_inventory_id=item_info_user.item_id,
                               item_quantity=item_info_user.item_quantity,
                               item_name=item_name,item_price=total_price, item_sold_at=datetime.now(ZoneInfo("Africa/Nairobi")))

    week_start_date = new_item.item_sold_at.date() - timedelta(days=new_item.item_sold_at.weekday())

    # updates in the dailySales table
    functions.update_dailysales_or_add_new_weekly_sale(db, new_item.item_inventory_id,
                                                       new_item.item_name, new_item.item_quantity,
                                                       total_price, new_item.item_sold_at.date())

    # updates in the weeklySales table
    functions.update_weeklysales_or_add_new_weekly_sale(db, new_item.item_inventory_id,
                                                        new_item.item_name, new_item.item_quantity,
                                                        total_price, week_start_date )

    #updates in the monthlySales table
    functions.update_monthly_sales_or_add_new_monthly_sale(db,new_item.item_inventory_id,
                                                           new_item.item_name, new_item.item_quantity,
                                                           total_price, new_item.item_sold_at.date())

    #updates in the yearlySales table
    functions.update_yearlysales_or_add_new_yearly_sale(db, new_item.item_inventory_id,
                                                        new_item.item_name, new_item.item_quantity,
                                                        total_price, new_item.item_sold_at.date())

    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    return new_item

@router.get("/", response_model=schemas.ItemSoldSalesResponse)
def get_sales(
    range: Annotated[Optional[str], Query(description="Filter: day, week, month, year")] = None,
    date_value: Annotated[Optional[date], Query(description="Reference date (YYYY-MM-DD)")] = None,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    today = datetime.now(UTC).date()
    base_date = date_value or today

    match range:
        case "day":
            item = db.query(models.DailySales).filter(models.DailySales.sale_date == base_date).all()

        case "week":
            start_of_week = base_date - timedelta(days=base_date.weekday())
            item = db.query(models.WeeklySales).filter(models.WeeklySales.week_start_date == start_of_week).all()

        case "month":
            start_of_month = base_date.replace(day=1)
            item = db.query(models.MonthlySales).filter(models.MonthlySales.sale_month == start_of_month).all()

        case "year":
            start_of_year = base_date.replace(day=1, month=1)
            item = db.query(models.YearlySales).filter(models.YearlySales.sale_year == start_of_year).all()

        case _:
            # Default fallback: today
            item = db.query(models.DailySales).filter(models.DailySales.sale_date == today).all()

    return {
        "items": item
    }

@router.get("/stats/total/", response_model=schemas.ItemSoldTotalPriceResponse)
def get_total_sales_for_given_time_period(db:Session = Depends(get_db), current_user = Depends(oauth2.get_current_user),
                                          range: Annotated[Optional[str], Query(description="Filter: day, week, month, year")] = None,
                                          date_value: Annotated[Optional[date], Query(description="reference_date (YYYY-MM-DD)")] = None,
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403,
                            detail="Admin access required")

    today = datetime.now(UTC).date()
    base_date = date_value or today

    match range:
        case "day":
            sales_query = db.query(func.sum(models.DailySales.total_price))
            total_sales = sales_query.filter(models.DailySales.sale_date == base_date).scalar() or 0
        case "week":
            start_of_week = base_date - timedelta(days=base_date.weekday())
            sales_query = db.query(func.sum(models.WeeklySales.total_price))
            total_sales = sales_query.filter(models.WeeklySales.week_start_date ==start_of_week).scalar()or 0
        case "month":
            start_of_month = base_date.replace(day=1)
            sales_query = db.query(func.sum(models.MonthlySales.total_price))
            total_sales = sales_query.filter(models.MonthlySales.sale_month == start_of_month).scalar() or 0
        case "year":
            start_of_year = base_date.replace(day=1, month=1)
            sales_query = db.query(func.sum(models.YearlySales.total_price))
            total_sales = sales_query.filter(models.YearlySales.sale_year == start_of_year).scalar() or 0
        case _:
            sales_query = db.query(func.sum(models.DailySales.total_price))
            total_sales = sales_query.filter(models.DailySales.sale_date == today).scalar() or 0

    return {"total_sales": total_sales}

@router.get("/stats/none/", response_model=List[schemas.ItemNoneSalesResponse])
def get_none_sales_over_given_period(
        range: Annotated[Optional[str], Query(description="Filter: day, week, month, year")] = None,
        date_value: Annotated[Optional[date], Query(description="reference_date (YYYY-MM-DD)")] = None,
        db: Session = Depends(get_db),
        current_user=Depends(oauth2.get_current_user)
):

    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")


    today = datetime.now(UTC).date()
    base_date = date_value or today

    match range:
        case "day":
            none_items = db.query(models.Item).outerjoin(models.DailySales, and_(
                models.DailySales.item_inventory_id == models.Item.item_id,
                models.DailySales.sale_date == base_date,
            )).filter(models.DailySales.item_inventory_id == None).all()
        case "week":
            none_items = db.query(models.Item).outerjoin(models.WeeklySales, and_(
                models.WeeklySales.item_inventory_id == models.Item.item_id,
                models.WeeklySales.week_start_date == base_date,
            )).filter(models.WeeklySales.item_inventory_id == None).all()
        case "month":
            none_items = db.query(models.Item).outerjoin(models.MonthlySales, and_(
                models.MonthlySales.item_inventory_id == models.Item.item_id,
                models.MonthlySales.sale_month == base_date,
            )).filter(models.MonthlySales.item_inventory_id == None).all()
        case "year":
            none_items = db.query(models.Item).outerjoin(models.YearlySales, and_(
                models.YearlySales.item_inventory_id == models.Item.item_id,
                models.YearlySales.sale_year == base_date,
            )).filter(models.YearlySales.item_inventory_id == None).all()
        case _:
            none_items = db.query(models.Item).outerjoin(models.DailySales, and_(
                models.DailySales.item_inventory_id == models.Item.item_id,
                models.DailySales.sale_date == today,
            )).filter(models.DailySales.item_inventory_id == None).all()


    return [schemas.ItemNoneSalesResponse.model_validate(item) for item in none_items]





@router.get("/{id}", response_model=schemas.ItemSaleResp)
def get_total_sales_for_day_for_specific_item(
    id:int,
    filter_date: Annotated[Optional[date], Query(description="Date of sale (YYYY-MM-DD)")] = None,
    db: Session = Depends(get_db),
    current_user = Depends(oauth2.get_current_user),
):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    item_db = db.query(models.ItemSold).filter(models.ItemSold.item_inventory_id == id).first()
    if item_db is None:
        raise HTTPException(status_code=404,
                            detail=f"Item with I.D {id} is not registered in inventory")
    query = db.query(models.ItemSold).filter(models.ItemSold.item_inventory_id == id)

    if filter_date:
       start_time_date = datetime.combine(filter_date, time.min).replace(tzinfo=timezone.utc)
       end_time_date = datetime.combine(filter_date, time.max).replace(tzinfo=timezone.utc)

    else:
        today = datetime.now(UTC).date()


    filtered_query = db.query(models.DailySales).filter(models.DailySales.sale_date == filter_date,
                                                        models.DailySales.item_inventory_id == id).first()

    print("I got here")
    return filtered_query
