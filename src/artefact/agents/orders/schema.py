import json
from typing import Literal

from pydantic import BaseModel, field_validator


class OrderItem(BaseModel):
    name: str
    quantity: int


class Order(BaseModel):
    order_id: int
    customer_first_name: str
    status: str
    order_date: str
    total_brl: float
    payment_method: str
    tracking_code: str | None
    estimated_delivery: str | None
    notes: str | None
    items: list[OrderItem]


class OrdersOutput(BaseModel):
    status: Literal["found", "not_found", "needs_identification"]
    order: Order | None

    @field_validator("order", mode="before")
    @classmethod
    def parse_json_string(cls, value):
        # The model sometimes sends the nested order as a JSON string, parsing it saves a retry round trip.
        if isinstance(value, str):
            return json.loads(value)
        return value
