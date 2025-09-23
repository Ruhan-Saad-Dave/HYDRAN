from fastapi import APIRouter 
from .models import UserQuery, QueryResponse
from .service import get_symptom_checker_response

symptom_router = APIRouter(
    tags=["symptom_checker"], 
)

@symptom_router.post("", response_model=QueryResponse)
@symptom_router.post("/", response_model=QueryResponse, include_in_schema=False)
async def create_query(query: UserQuery):
    response = get_symptom_checker_response(query.session_id, query.query)
    return QueryResponse(response=response)