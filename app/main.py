
from fastapi import FastAPI
from app.api import ussd_routes, payment_routes, admin_routes

app = FastAPI(title="Uduma Connect API")

# include routes
app.include_router(ussd_routes.router)
app.include_router(payment_routes.router)
app.include_router(admin_routes.router)

@app.get("/")
def home():
    return {"message": "huduma Connect backend running"}