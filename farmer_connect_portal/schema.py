from pydantic import BaseModel


class Product(BaseModel):
    id: int
    farmer_id: int
    product_name: str
    quantity: float
    price_per_kg: float
    location: str

    class Config:
        from_attributes = True


class BuyItemForm(BaseModel):
    farmer_id: str
    product_name: str
    quantity: str
    location: str
    price_per_kg: str
