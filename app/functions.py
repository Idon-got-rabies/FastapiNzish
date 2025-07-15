import datetime
from sqlalchemy import Date
from fastapi import FastAPI, Response, status,HTTPException
from sqlalchemy.orm import Session
from app import models
from passlib.context import CryptContext

from app.models import WeeklySales, DailySales, MonthlySales, YearlySales

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")



def calculate_total_price(db: Session, id: int, quantity: int):
    item_query = db.query(models.Item).filter(models.Item.item_id == id).first()
    if item_query is None:
        raise HTTPException(status_code=404, detail="Requested item was not found")

    total_price = item_query.item_price * quantity
    return total_price

def update_itemsold_name(db:Session, id: int, update_data: dict):
    item_query = db.query(models.ItemSold).filter(models.ItemSold.item_inventory_id == id)
    items_db = item_query.all()

    if items_db is None:
        raise HTTPException(status_code=404,
                            detail=f"Requested item with id {id} was not found")

    item_query.update(update_data, synchronize_session=False)
    db.commit()
    updated_name = item_query.first()
    return updated_name


def update_dailysales_name(db:Session, id: int, update_data: dict):
    item_query = db.query(models.DailySales).filter(models.DailySales.item_inventory_id == id)
    items_db = item_query.all()

    if items_db is None:
        raise HTTPException(status_code=404,
                            detail=f"Requested item with id {id} was not found")

    item_query.update(update_data, synchronize_session=False)
    db.commit()
    updated_name = item_query.first()
    return updated_name


def update_weeklysales_name(db:Session, id: int, update_data: dict):
    item_query = db.query(models.WeeklySales).filter(models.WeeklySales.item_inventory_id == id)
    items_db = item_query.all()

    if items_db is None:
        raise HTTPException(status_code=404,
                            detail=f"Requested item with id {id} was not found")

    item_query.update(update_data, synchronize_session=False)
    db.commit()
    updated_name = item_query.first()
    return updated_name

def update_dailysales_or_add_new_weekly_sale(db: Session, id:int,
                                             item_name: str, quantity: int,
                                             total_sales: int, sale_date: datetime):

    exists = db.query(models.DailySales).filter(models.DailySales.item_inventory_id == id,
                                                models.DailySales.sale_date == sale_date).first()

    if exists:
        exists.total_quantity_sold += quantity
        exists.total_price += total_sales

    else:

        new_daily_sale = DailySales(item_inventory_id=id, item_name=item_name,
                                    total_price=total_sales, total_quantity_sold=quantity,
                                    sale_date=sale_date)
        db.add(new_daily_sale)

    db.commit()


def update_weeklysales_or_add_new_weekly_sale(db: Session, id: int,
                                              item_name: str, quantity: int,
                                              total_sales: int, week_start_date: datetime):

    exists = db.query(models.WeeklySales).filter(models.WeeklySales.item_inventory_id == id,
                                                  models.WeeklySales.week_start_date == week_start_date).first()


    if exists:
        exists.total_quantity_sold += quantity
        exists.total_price += total_sales

    else:

        new_weekly_sales = WeeklySales(
            item_inventory_id=id,
            item_name=item_name,
            total_price=total_sales,
            total_quantity_sold=quantity,
            week_start_date= week_start_date

        )
        db.add(new_weekly_sales)

    db.commit()

def update_monthly_sales_or_add_new_monthly_sale(db: Session, id: int,
                                                 item_name: str, quantity: int,
                                                 total_sales: int, sale_month_date: datetime):

    sale_month = sale_month_date.replace(day=1)

    exists = db.query(models.MonthlySales).filter(models.MonthlySales.item_inventory_id == id,
                                                  models.MonthlySales.sale_month == sale_month).first()
    if exists:
        exists.total_quantity_sold += quantity
        exists.total_price += total_sales

    else:
        new_monthly_sales = MonthlySales(
            item_inventory_id=id,
            item_name=item_name,
            total_price=total_sales,
            total_quantity_sold=quantity,
            sale_month=sale_month
        )
        db.add(new_monthly_sales)

    db.commit()

def update_yearlysales_or_add_new_yearly_sale(db: Session, id: int,
                                              item_name: str, quantity: int,
                                              total_sales: int, sale_year_date: datetime):

    sale_year = sale_year_date.replace(month=1, day=1)

    exists = db.query(models.YearlySales).filter(models.YearlySales.item_inventory_id == id,
                                                 models.YearlySales.sale_year == sale_year).first()

    if exists:
        exists.total_quantity_sold += quantity
        exists.total_price += total_sales

    else:
        new_yearly_sale = YearlySales(
            item_name=item_name,
            item_inventory_id=id,
            total_price=total_sales,
            total_quantity_sold=quantity,
            sale_year=sale_year
        )
        db.add(new_yearly_sale)

    db.commit()

def update_item_by_id(db: Session, id: int,update_data: dict):


    item_query = db.query(models.Item).filter(models.Item.item_id == id)
    item_db = item_query.first()

    if item_db is None:
        raise HTTPException(status_code=404, detail="Requested item was not found")

    item_query.update(update_data, synchronize_session=False)
    db.commit()

    updated_item = item_query.first()

    return  updated_item

def update_pass_by_user_id(db:Session, id:int, update_data: dict):
    user_query = db.query(models.User).filter(models.User.user_id == id)
    user_db = user_query.first()
    if user_db is None:
        raise HTTPException(status_code=404, detail="Requested user was not found")

    user_query.update(update_data, synchronize_session=False)
    db.commit()
    return {"Data: success"}


def hash_password(user_password: str):

    return pwd_context.hash(user_password)

def compare_password(hashed_password: str, user_password: str):
    return pwd_context.verify(user_password, hashed_password)