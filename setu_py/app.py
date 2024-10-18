from fastapi import FastAPI, HTTPException
from .db import Database
from contextlib import asynccontextmanager

# Initialize the Database class
db = Database()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the connection pool on startup
    db.initialize_pool()
    yield
    # Close the connection pool on shutdown
    db.close_pool()

app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI with PostgreSQL"}

@app.get("/users")
def get_users(ref: str):
    conn = None
    try:
        # Get a connection from the pool
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute(f"""
            SELECT id, slug, variant_reference, images, is_canonical, specifications FROM watch_model_data
            WHERE model_reference = '{ref}';
        """)
        users = cur.fetchall()
        cur.close()
        return {"users": users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            # Return the connection to the pool
            db.return_connection(conn)
