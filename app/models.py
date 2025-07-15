import datetime

from .database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, column, Date
from sqlalchemy.sql.sqltypes import TIMESTAMP, Boolean
from sqlalchemy.sql.expression import text

class Item(Base):
    __tablename__ = "items_inventory"

    item_id = Column(Integer, primary_key=True, nullable=False)
    item_name = Column(String, nullable=False)
    item_quantity = Column(Integer, nullable=False)
    item_price = Column(Integer, nullable=False)

class ItemSold(Base):
    __tablename__ = "items_sold"
    item_id = Column(Integer, primary_key=True,nullable=False)
    item_name = Column(String, nullable=False)
    item_quantity = Column(Integer, nullable=False)
    item_price = Column(Integer, nullable=False)
    item_sold_at = Column(TIMESTAMP(timezone=True),
                          nullable=False,
                          server_default=text('now()'))

    item_inventory_id = Column(Integer,
                               ForeignKey("items_inventory.item_id",ondelete= "NO ACTION"),
                               nullable=False)

class Sales(Base):
    __abstract__ = True
    item_id = Column(Integer, primary_key=True, nullable=False)
    item_name = Column(String, nullable=False)
    total_quantity_sold = Column(Integer, nullable=False)
    total_price = Column(Integer, nullable=False)
    item_inventory_id = Column(Integer, ForeignKey("items_inventory.item_id",ondelete= "NO ACTION"), nullable=False)

class DailySales(Sales):
    __tablename__ = "daily_sales"

    sale_date = Column(Date, nullable=False)

    __table_args__ = (
        UniqueConstraint("item_inventory_id", "sale_date", "item_name", name="uix_item_daily"),
    )
    model_config = {
        "from_attributes": True
    }



class WeeklySales(Sales):
    __tablename__ = "weekly_sales"

    week_start_date = Column(Date, nullable=False)

    __table_args__ = (
        UniqueConstraint("item_inventory_id", "week_start_date", "item_name", name="uix_item_week"),
    )

class MonthlySales(Sales):
    __tablename__ = "monthly_sales"

    sale_month = Column(Date, nullable=False )

    __table_args__ = (
        UniqueConstraint("item_inventory_id", "sale_month", "item_name", name="uix_item_month"),

    )

class YearlySales(Sales):
    __tablename__ = "yearly_sales"
    sale_year = Column(Date, nullable=False )

    __table_args__ = (
       UniqueConstraint("item_inventory_id", "sale_year","item_name", name="uix_item_year"),

    )


class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, nullable=False)
    user_email = Column(String, nullable=False, unique=True)
    user_password = Column(String, nullable=False)
    is_admin = Column(Boolean, nullable=False, server_default=text("False"))


class AdminUser(Base):
    __tablename__ = "admin_users"
    user_id = Column(Integer, primary_key=True, nullable=False)
    user_email = Column(String, nullable=False, unique=True)
    user_password = Column(String, nullable=False)
    is_admin = Column(Boolean, nullable=False, server_default=text("True"))

