from fastapi import APIRouter

from view.v1.user import router as user_router
from view.v1.currency import router as currency_router
from view.v1.exchange_rate import router as exchange_rate_router
from view.v1.brand import router as brand_router
from view.v1.matrix_type import router as matrix_type_router
from view.v1.os import router as os_router
from view.v1.shop import router as shop_router
from view.v1.screen_resolution import router as screen_resolution_router
from view.v1.tv import router as tv_router
from view.v1.shop_link import router as shop_link_router
from view.v1.day_price import router as day_price_router
from view.v1.file_upload import router as file_upload_router
from view.v1.filters import router as filters_router


v1_router = APIRouter()
v1_router.include_router(user_router)
v1_router.include_router(currency_router)
v1_router.include_router(exchange_rate_router)
v1_router.include_router(brand_router)
v1_router.include_router(matrix_type_router)
v1_router.include_router(os_router)
v1_router.include_router(shop_router)
v1_router.include_router(screen_resolution_router)
v1_router.include_router(tv_router)
v1_router.include_router(shop_link_router)
v1_router.include_router(day_price_router)
v1_router.include_router(file_upload_router)
v1_router.include_router(filters_router)
