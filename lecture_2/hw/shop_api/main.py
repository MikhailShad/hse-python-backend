from fastapi import FastAPI

from lecture_2.hw.shop_api.routes.cart_routes import router as cart_router
from lecture_2.hw.shop_api.routes.item_routes import router as item_router

app = FastAPI(title="Shop API")

app.include_router(item_router)
app.include_router(cart_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
