# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import os
from supabase import create_client, Client

# Initialize Supabase client
# Ensure SUPABASE_URL and SUPABASE_KEY are set as environment variables
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

app = FastAPI()

class MedicineStock(BaseModel):
    id: int
    name: str
    quantity: int
    last_updated: datetime

class SyncRequest(BaseModel):
    last_synced_at: Optional[datetime] = None

class SyncResponse(BaseModel):
    data: List[MedicineStock]
    server_time: datetime

@app.post("/sync/stock", response_model=SyncResponse)
async def sync_stock(request: SyncRequest):
    """
    Synchronizes medicine stock data with the client.
    Sends only the data that has changed since the last sync.
    """
    last_synced_at = request.last_synced_at
    server_time = datetime.utcnow()

    query = supabase.from_('medicine_stock').select("*")

    if last_synced_at:
        # Fetch only data updated after the last sync timestamp
        query = query.gte("last_updated", last_synced_at.isoformat())

    try:
        response = query.execute()
        
        # Supabase returns data in the 'data' key
        stock_data = response.data
        
        # Convert dictionary data to Pydantic model instances
        medicines = [MedicineStock(**item) for item in stock_data]
        
        return SyncResponse(data=medicines, server_time=server_time)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))