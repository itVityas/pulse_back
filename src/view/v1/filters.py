from fastapi import APIRouter, status, Depends, HTTPException

from settings.database import get_session
from repository.shop import ShopData


router = APIRouter(prefix='/filters', tags=['Filters'],)


@router.get('/main/', status_code=status.HTTP_200_OK)
async def get_main_filters(session=Depends(get_session)):
    try:
        rez_dict = {}

        shops_obj, _ = await ShopData(session).get_multi(limit=-1)
        buf_shops = [{'id': shop.id, 'name': shop.name} for shop in shops_obj]
        rez_dict['shops'] = {
                'title': 'Магазины',
                'search_name': 'shops',
                'values': buf_shops,
                'type': 'checkbox'
            }

        return rez_dict
    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ex))
