from dataclasses import field
from datetime import datetime

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from fastapi import Query
from sqlalchemy.sql.operators import from_


class ItemInventory(BaseModel):
    itemInven_name: str = Field(..., alias="item_name")
    itemInven_quantity: int = Field(..., alias="item_quantity")
    itemInven_price: float = Field(..., alias="item_price")


    model_config = {
        "populate_by_name": True,
        "from_attributes": True
    }

class ItemInven(ItemInventory):

    itemInven_id: int = Field(..., alias="item_id")


class ItemInventoryLowStockResponse(BaseModel):
    item_name: str
    item_id: int
    item_quantity: int

    model_config = {
        "from_attributes": True
    }


class ItemInventoryResponse(ItemInventory):
    pass


class UpdateItemInventory(ItemInventory):
    pass

class UpdateItemInventoryName(BaseModel):
    itemInven_name: str = Field(..., alias="item_name")

    model_config = {
        "populate_by_name": True,
        "from_attributes": True
    }

class UpdateItemInventoryQuantity(BaseModel):
    itemInven_quantity: int = Field(..., alias="item_quantity")

    model_config = {
        "populate_by_name": True,
        "from_attributes": True
    }

class UpdateItemInventoryPrice(BaseModel):
    itemInven_price: float = Field(..., alias="item_price")

    model_config = {
        "populate_by_name": True,
        "from_attributes": True
    }


class ItemSold(BaseModel):
    item_id: int = Field(..., alias="item_id")
    item_quantity: int = Field(..., alias="total_items_sold")

    model_config = {
        "populate_by_name": True,
        "from_attributes": True
    }

class ItemNoneSalesResponse(BaseModel):
    item_name:str
    item_id: int

    model_config = {
        "from_attributes": True
    }


class ItemSoldResponse(BaseModel):
    item_name: str
    item_quantity: int
    item_sold_at: datetime
    item_price: float
    item_inventory_id: int

    model_config = {
        "from_attributes": True
    }

class ItemSoldFetchResponse(BaseModel):
    items: List[ItemSoldResponse]
    total_sales: float

class ItemSaleResp(BaseModel):
    item_name: str
    item_id: int
    item_inventory_id: int
    total_quantity_sold: int
    total_price: int

    model_config = {
        "from_attributes": True
    }


class ItemSoldSalesResponse(BaseModel):
    items: List[ItemSaleResp]

    model_config = {
        "from_attributes": True
    }

class ItemSoldTotalPriceResponse(BaseModel):
    total_sales: int

    model_config = {
        "from_attributes": True
    }

class UserCreate(BaseModel):
    user_email: EmailStr
    user_password: str

class UserCreateResponse(BaseModel):
    user_email: EmailStr

class UserUpdatePassword(BaseModel):
    user_password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class AccessToken(BaseModel):
    access_token: str
    token_type: str

class AccessTokenData(BaseModel):
    user_id: Optional[int] = None
    is_admin: Optional[bool] = None