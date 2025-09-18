import os
from supabase import create_client, Client

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

#fetch data, limit 1000 row
response = (
    supabase.table("planets")
    .select("*")
    .execute()
)

#insert data
response = (
    supabase.table("planets")
    .insert({"id": 1, "name": "Pluto"})
    .execute()
)

#update data
response = (
    supabase.table("instruments")
    .update({"name": "piano"})
    .eq("id", 1)
    .execute()
)

#delete data
response = (
    supabase.table("countries")
    .delete()
    .eq("id", 1)
    .execute()
)