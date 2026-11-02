# Run using: uvicorn main:app --reload
# API documentation: http://127.0.0.1:8000/docs

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from fastapi.middleware.cors import CORSMiddleware
import models, schemas
import logging

# Create all tables in the database
models.Base.metadata.create_all(bind=engine)

# Create log file
logging.basicConfig(
    filename='server.log',
    encoding='utf-8',
    level=logging.DEBUG
)

# Create the FastAPI application
app = FastAPI()

# Add CORS middleware to allow React frontend to connect
app.add_middleware(
    CORSMiddleware,
    # Local dev server, or a page served over http from a plain IP (the VM's nginx)
    allow_origin_regex=r"http://(localhost:3000|\d{1,3}(\.\d{1,3}){3})",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ROOT
@app.get("/")
def read_root():
    return {"message": "Use the RESTful API"}


# CREATE - Add a new item
@app.post("/items/", response_model=schemas.Item)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    logging.info("CREATE : %s", item)

    db_item = models.Item(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


# READ - Get all items
@app.get("/items/", response_model=list[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    logging.info("READ ALL : skip=%s limit=%s", skip, limit)

    items = db.query(models.Item).offset(skip).limit(limit).all()
    return items


# READ - Get a single item by ID
@app.get("/items/{item_id}", response_model=schemas.Item)
def read_item(item_id: int, db: Session = Depends(get_db)):
    logging.info("READ ONE : %s", item_id)

    item = db.query(models.Item).filter(models.Item.id == item_id).first()

    if item is None:
        logging.error("READ ONE : Item %s not found", item_id)
        raise HTTPException(status_code=404, detail="Item not found")

    return item


# UPDATE - Update an existing item
@app.put("/items/{item_id}", response_model=schemas.Item)
def update_item(
    item_id: int,
    item: schemas.ItemCreate,
    db: Session = Depends(get_db)
):
    logging.info("UPDATE : item_id=%s new data={%s}", item_id, item)

    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()

    if db_item is None:
        logging.error("UPDATE : Item %s not found", item_id)
        raise HTTPException(status_code=404, detail="Item not found")

    for field, value in item.dict().items():
        setattr(db_item, field, value)

    db.commit()
    db.refresh(db_item)
    return db_item


# DELETE - Remove an item
@app.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    logging.info("DELETE : %s", item_id)

    item = db.query(models.Item).filter(models.Item.id == item_id).first()

    if item is None:
        logging.error("DELETE : Item %s not found", item_id)
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(item)
    db.commit()
    return {"message": "Item deleted successfully"}