from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 

from features.symptom_checker.router import symptom_router
from features.stock.router import stock_router

app = FastAPI(
    title = "HYDRAN Telemedicine API",
    description = "API to perform telemedicine operations",
    version = "0.1.0",
    docs_url = "/docs",
    redoc_url = "/redoc",
)

app.add_middleware(
    CORSMiddleware,  #CORS = Cross Origin Resource Sharing
    allow_origins = ["*"], #allow all origins
    allow_credentials = True, #send credentials
    allow_methods = ["*"], #use any api type method
    allow_headers = ["*"], #additional information
)

app.include_router(symptom_router, prefix = "/symptom_checker")
app.include_router(stock_router, prefix = "/stock_checker")

if __name__ == "__main__":
    import uvicorn 
    uvicorn.run("main:app", host = "0.0.0.0", port = 8000, reload = True)

