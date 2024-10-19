from fastapi import FastAPI, HTTPException
from .db import Database
from contextlib import asynccontextmanager
from fastapi.responses import ORJSONResponse
from psycopg2.extras import RealDictCursor
import orjson

# Initialize the Database class
db = Database()

class CustomUJSONResponse(ORJSONResponse):
    def render(self, content) -> bytes:
        return orjson.dumps(content)

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

@app.get("/ref", response_class=CustomUJSONResponse)
def get_ref(ref: str):
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

@app.get("/id", response_class=CustomUJSONResponse)
def get_id(id: int):
    conn = None
    try:
        # Get a connection from the pool
        conn = db.get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(f"""
            SELECT * FROM watch_model_data
            WHERE id = {id};
        """)
        model = cur.fetchone()
        cur.execute(f"""
            SELECT * FROM watch_collection_data
            WHERE id = {model["watch_collection_id"]};
        """)
        col = cur.fetchone()
        model["watch_collection_data"] = col
        cur.close()
        return model
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            # Return the connection to the pool
            db.return_connection(conn)
