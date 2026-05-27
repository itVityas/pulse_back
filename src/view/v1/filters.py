from fastapi import APIRouter, status, Depends, HTTPException

from settings.database import get_session
from repository.shop import ShopData
from repository.brand import BrandData
from repository.os import OSData
from repository.screen_resolution import ScreenResolutionData
from repository.matrix_type import MatrixTypeData
from repository.currency import CurrencyData


router = APIRouter(prefix='/filters', tags=['Filters'],)


@router.get('/main/', status_code=status.HTTP_200_OK)
async def get_main_filters(session=Depends(get_session)):
    try:
        rez_dict = []

        shops_obj, _ = await ShopData(session).get_multi(limit=-1)
        buf_shops = [shop.name for shop in shops_obj]
        rez_dict.append({
                'title': 'Магазины',
                'search_name': 'shops',
                'values': buf_shops,
                'type': 'checkbox'
            })

        brands_obj, _ = await BrandData(session).get_multi(limit=-1)
        buf_brands = [brand.name for brand in brands_obj]
        rez_dict.append({
                'title': 'Бренды',
                'search_name': 'brands',
                'values': buf_brands,
                'type': 'checkbox'
            })

        os_obj, _ = await OSData(session).get_multi(limit=-1)
        buf_os = [os.name for os in os_obj]
        rez_dict.append({
                'title': 'Операционные системы',
                'search_name': 'os',
                'values': buf_os,
                'type': 'checkbox'
            })

        screen_resolutions_obj, _ = await ScreenResolutionData(session).get_multi(limit=-1)
        buf_screen_resolutions = [screen_resolution.name for screen_resolution in screen_resolutions_obj]
        rez_dict.append({
                'title': 'Разрешения экрана',
                'search_name': 'screen_resolutions',
                'values': buf_screen_resolutions,
                'type': 'radiobutton'
            })

        matrix_types_obj, _ = await MatrixTypeData(session).get_multi(limit=-1)
        buf_matrix_types = [matrix_type.name for matrix_type in matrix_types_obj]
        rez_dict.append({
                'title': 'Типы матриц',
                'search_name': 'matrix_types',
                'values': buf_matrix_types,
                'type': 'checkbox'
            })

        rez_dict.append({
            'title': 'Частота обновления',
            'search_name': 'refresh_rate',
            'values': [50, 60, 120, 144],
            'type': 'radiobutton'
        })

        rez_dict.append({
            'title': 'Диагональ',
            'search_name': 'diagonal',
            'values': {'min': 24, 'max': 110},
            'type': 'range'
        })

        currency_obj, _ = await CurrencyData(session).get_multi(limit=-1)
        buf_currency = [currency.name for currency in currency_obj]
        rez_dict.append({
                'title': 'Валюта',
                'search_name': 'currency',
                'values': buf_currency,
                'type': 'radiobutton'
            })

        return rez_dict
    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ex))
