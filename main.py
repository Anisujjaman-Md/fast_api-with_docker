import asyncpg
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# Define your PostgreSQL connection URL
# Define your PostgreSQL connection URL
DATABASE_URL = "postgresql://your_postgres_user:your_postgres_password@db/your_database_name"


# Define an asynchronous function to connect to the database
async def connect_to_database():
    try:
        # Connect to the database
        pool = await asyncpg.create_pool(DATABASE_URL)
        # Return the connection pool
        return pool
    except Exception as e:
        print(f"Error connecting to the database: {e}")

# Use dependency injection to inject the database connection pool into your route handlers
@app.on_event("startup")
async def startup_event():
    app.pool = await connect_to_database()
    if app.pool is None:
        print("Failed to connect to the database.")  # Add more detailed logging here if needed.

@app.on_event("shutdown")
async def shutdown_event():
    if app.pool is not None:
        await app.pool.close()

# Define Pydantic model for Item
class Item(BaseModel):
    name: str
    description: str = None
    price: float
    quantity: int

# Item creation API endpoint
@app.post("/items/")
async def create_item(item: Item):
    if app.pool is None:
        raise HTTPException(status_code=500, detail="Database connection not established.")
    
    async with app.pool.acquire() as connection:
        try:
            # Insert item into the database
            await connection.execute(
                "INSERT INTO items (name, description, price, quantity) VALUES ($1, $2, $3, $4)",
                item.name, item.description, item.price, item.quantity
            )
            return {"message": "Item created successfully"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error creating item: {str(e)}")

# Item retrieval API endpoint
@app.get("/items/")
async def read_items():
    if app.pool is None:
        raise HTTPException(status_code=500, detail="Database connection not established.")
    
    async with app.pool.acquire() as connection:
        try:
            # Fetch all items from the database
            result = await connection.fetch("SELECT * FROM items")
            return {"items": result}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving items: {str(e)}")
