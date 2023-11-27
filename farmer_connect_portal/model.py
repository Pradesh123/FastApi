from database import Base
from sqlalchemy import Column, String, INTEGER, FLOAT, ForeignKey


class Farmer(Base):
    __tablename__ = "farmer_details"
    id = Column(INTEGER, primary_key=True, index=True)
    name = Column(String)
    password = Column(String)
    mail_id = Column(String)
    contact_no = Column(String)


class Consumer(Base):
    __tablename__ = "consumer_details"
    id = Column(INTEGER, primary_key=True, index=True)
    name = Column(String)
    password = Column(String)
    mail_id = Column(String)
    contact_no = Column(String)


class Retailer(Base):
    __tablename__ = "retailer_details"
    id = Column(INTEGER, primary_key=True, index=True)
    name = Column(String)
    password = Column(String)
    mail_id = Column(String)
    contact_no = Column(String)


class ProductDetails(Base):
    __tablename__ = "product_details"
    id = Column(INTEGER, primary_key=True, index=True)
    farmer_id = Column(INTEGER, ForeignKey("farmer_details.id"))
    product_name = Column(String)
    quantity = Column(FLOAT)
    price_per_kg = Column(FLOAT)
    location = Column(String)


class SoldProducts(Base):
    __tablename__ = "sold_product_details"
    id = Column(INTEGER, primary_key=True, index=True)
    buyer_id = Column(INTEGER)
    farmer_id = Column(INTEGER)
    product_name = Column(String)
    quantity = Column(FLOAT)
    price_per_kg = Column(FLOAT)
    location = Column(String)
    total_amount = Column(FLOAT)
