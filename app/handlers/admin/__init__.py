from aiogram import Router
from .panel import router as panel_router
from .products import router as products_router
from .branches import router as branches_router

router = Router()
router.include_router(panel_router)
router.include_router(products_router)
router.include_router(branches_router)
