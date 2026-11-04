import re

import pandas as pd

from artefact.data.loader import load_csv

NOT_FOUND = {"status": "not_found", "order": None}


def digits(text: str) -> str:
    return re.sub(r"\D", "", text)


def is_same_customer(customer: pd.Series, email_or_phone: str) -> bool:
    value = email_or_phone.strip()
    if "@" in value:
        return value.casefold() == customer["email"].casefold()

    # Compare the last 8 digits, so the number matches with or without the area code
    value_digits = digits(value)
    if len(value_digits) < 8:
        return False
    return value_digits[-8:] == digits(customer["phone"])[-8:]


def optional(value) -> str | None:
    if pd.isna(value):
        return None
    return value


def get_order(order_id: int, email_or_phone: str) -> dict:
    orders = load_csv("orders")
    matches = orders[orders["order_id"] == order_id]
    if matches.empty:
        return NOT_FOUND
    order = matches.iloc[0]

    customers = load_csv("customers")
    customer = customers[customers["customer_id"] == order["customer_id"]].iloc[0]
    # Same answer for a wrong order id or a wrong email/phone, so nobody can probe other customers' orders
    if not is_same_customer(customer, email_or_phone):
        return NOT_FOUND

    order_items = load_csv("order_items")
    order_items = order_items[order_items["order_id"] == order_id]
    products = load_csv("products")[["product_id", "name"]]
    items = []
    for _, item in order_items.merge(products, on="product_id").iterrows():
        items.append({"name": item["name"], "quantity": int(item["quantity"])})

    # total_brl is what the customer paid, never recompute it from current prices
    return {
        "status": "found",
        "order": {
            "order_id": int(order["order_id"]),
            "customer_first_name": customer["name"].split()[0],
            "status": order["status"],
            "order_date": order["order_date"],
            "total_brl": float(order["total_brl"]),
            "payment_method": order["payment_method"],
            "tracking_code": optional(order["tracking_code"]),
            "estimated_delivery": optional(order["estimated_delivery"]),
            "notes": optional(order["notes"]),
            "items": items,
        },
    }
