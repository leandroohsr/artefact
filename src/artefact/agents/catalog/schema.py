from pydantic import BaseModel


class Product(BaseModel):
    name: str
    category: str
    price_brl: float
    final_price_brl: float
    stock: int
    status: str
    promotion: str | None


class CatalogOutput(BaseModel):
    products: list[Product]
    notes: str
