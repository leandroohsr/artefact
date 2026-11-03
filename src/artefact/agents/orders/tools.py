from langchain_core.tools import tool

from artefact.data import orders as orders_data


@tool
def get_order_status(order_id: int, email_or_phone: str) -> dict:
    """Look up one order. Returns it only if email_or_phone belongs to the customer who placed it;
    otherwise returns {"status": "not_found"} without saying which value was wrong.

    Args:
        order_id: the order number given by the customer, e.g. 7.
        email_or_phone: the customer's e-mail or phone, exactly as they wrote it.
    """
    return orders_data.get_order(order_id, email_or_phone)
