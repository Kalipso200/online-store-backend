from fastapi import APIRouter
from app.api.routes import auth, products, categories, reviews, cart, promotions, admin

api_router = APIRouter()

# Группируем роуты по функциональности
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(products.router, prefix="/products", tags=["Products"])
api_router.include_router(categories.router, prefix="/categories", tags=["Categories"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["Reviews"])
api_router.include_router(cart.router, prefix="/cart", tags=["Cart"])
api_router.include_router(promotions.router, prefix="/promotions", tags=["Promotions"])
api_router.include_router(admin.router, prefix="/admin", tags=["Administration"])
