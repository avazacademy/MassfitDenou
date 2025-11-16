from aiogram import Router
from .products import router as products_router
from .basket import router as basket_router
from .orders import router as orders_router

router = Router()
router.include_router(products_router)
router.include_router(basket_router)
router.include_router(orders_router)
