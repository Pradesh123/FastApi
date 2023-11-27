import fastapi
from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from sqlalchemy import update, delete, and_

import model
from database import engine, session_local
from typing import Annotated
from sqlalchemy.orm import Session

app = FastAPI()
app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent.parent.absolute() / "r_proj" / "static"),
    name="static",
)

templates = Jinja2Templates(directory="templates")

# below line will create tables in database
model.Base.metadata.create_all(bind=engine)


# db connection
def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.post("/sign_in")
async def sign_in(request: Request):
    return templates.TemplateResponse("sign_in.html", {"request": request})


@app.post("/sign_up")
async def sign_up(request: Request):
    return templates.TemplateResponse("sign_up.html", {"request": request})


@app.post("/sign_up_submit")
async def handle_sign_up_submit(request: Request, db: db_dependency, username: str = Form(...), password: str = Form(...), email: str = Form(...), contact_number: str = Form(...),
                                user_type: str = Form(...)):
    if user_type == "Farmer":
        user_details = model.Farmer(name=username, password=password, mail_id=email, contact_no=contact_number)
    elif user_type == "Consumer":
        user_details = model.Consumer(name=username, password=password, mail_id=email, contact_no=contact_number)
    else:
        user_details = model.Retailer(name=username, password=password, mail_id=email, contact_no=contact_number)
    db.add(user_details)
    db.commit()
    db.refresh(user_details)
    return templates.TemplateResponse("sign_in.html", {"request": request, "message": "Account Creation Success"})


@app.post("/sign_in_submit")
async def handle_sign_in_submit(request: Request, db: db_dependency, username: str = Form(...), password: str = Form(...), user_type: str = Form(...)):
    look_up_table = None
    if user_type == "Farmer":
        look_up_table = model.Farmer
    elif user_type == "Consumer":
        look_up_table = model.Consumer
    else:
        look_up_table = model.Retailer

    result = db.query(look_up_table).filter(look_up_table.name == username).first()
    if result:
        result = db.query(look_up_table).filter(look_up_table.password == password).first()
    else:
        raise HTTPException(status_code=404, detail="Invalid UserName")
    if result:
        if user_type == "Farmer":
            farmer_record = db.query(model.Farmer).filter(model.Farmer.name == username).first()
            return templates.TemplateResponse("farmer_post_data.html", {"request": request, "message": "Logged in Successfully", "farmer_id": farmer_record.id})
        elif user_type == "Consumer":
            farmer_products = db.query(model.ProductDetails).filter(model.ProductDetails.quantity <= 50).all()
            current_user_id = db.query(model.Consumer).filter(model.Consumer.name == username).first().id
            return templates.TemplateResponse("products_for_consumer.html", {"request": request, "farmer_products": farmer_products, "current_user_id": current_user_id, "user_type": "Consumer"})
        else:
            farmer_products = db.query(model.ProductDetails).filter(model.ProductDetails.quantity > 50).all()
            current_user_id = db.query(model.Retailer).filter(model.Retailer.name == username).first().id
            return templates.TemplateResponse("products_for_retailer.html", {"request": request, "farmer_products": farmer_products, "current_user_id": current_user_id, "user_type": "Retailer"})
    else:
        raise HTTPException(status_code=404, detail="Invalid Password")


@app.post("/farmer_items_submit")
async def post_items(request: Request, db: db_dependency, product_name: str = Form(...), quantity: float = Form(...), price: float = Form(...), location: str = Form(...), farmer_id: int = Form(...)):
    product_details = model.ProductDetails(product_name=product_name, quantity=quantity, price_per_kg=price, location=location, farmer_id=farmer_id)
    db.add(product_details)
    db.commit()
    db.refresh(product_details)
    return templates.TemplateResponse("farmer_post_data.html", {"request": request, "message": "Logged in Successfully", "farmer_id": farmer_id})


@app.post("/buy")
async def buy_products(request: Request, farmer_id: int = Form(...), product_name: str = Form(...), quantity: float = Form(...), location: str = Form(...), price_per_kg: float = Form(...),
                       current_user_id: str = Form(...), user_type: str = Form(...)):
    return templates.TemplateResponse("payment.html", {"request": request, "id": current_user_id, "user_type": user_type,
                                                       "farmer_id": farmer_id, "product_name": product_name, "quantity": quantity, "price_per_kg": price_per_kg,
                                                       "location": location})


# need to create sold table
@app.post("/payment")
async def payment(request: Request, db: db_dependency, current_user_id: str = Form(...), user_type: str = Form(...), farmer_id: int = Form(...),
                  product_name: str = Form(...), quantity: float = Form(...), price_per_kg: float = Form(...), location: str = Form(...)):
    print("current_user_id: ", current_user_id)
    print("user_type: ", user_type)
    print(farmer_id)
    print(product_name)
    print(quantity)
    print(price_per_kg)
    print(location)
    sold_item = db.query(model.ProductDetails).filter(model.ProductDetails.farmer_id == farmer_id and model.ProductDetails.product_name == product_name
                                                      and model.ProductDetails.price_per_kg == price_per_kg and model.ProductDetails.quantity == quantity).first()
    # db.execute(update(model.ProductDetails).values(product_name='new value'))
    # db.execute(delete(model.ProductDetails).where(and_(model.ProductDetails.farmer_id == farmer_id, model.ProductDetails.product_name == product_name
    #                                                    , model.ProductDetails.quantity == quantity, model.ProductDetails.price_per_kg == price_per_kg
    #                                                    , model.ProductDetails.location == location)))
    db.query(model.ProductDetails).filter_by(
        farmer_id=farmer_id,
        # product_name=product_name,
        quantity=quantity,
        price_per_kg=price_per_kg,
        location=location
    ).delete()
    db.add(model.SoldProducts(buyer_id=current_user_id, farmer_id=farmer_id, product_name=product_name,
                              quantity=quantity, price_per_kg=price_per_kg, location=location, total_amount=(quantity * price_per_kg)))
    db.commit()
    farmer_products = db.query(model.ProductDetails).filter(model.ProductDetails.quantity > 50).all()
    if not farmer_products:
        farmer_products = None
    return templates.TemplateResponse("products_for_retailer.html", {"request": request, "farmer_products": farmer_products, "current_user_id": current_user_id, "user_type": "Retailer"})
