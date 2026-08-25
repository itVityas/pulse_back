import csv
import io

from fastapi import Depends, APIRouter, status
from fastapi.responses import Response

from share.my_exception import MyHttpException
from settings.database import get_session
from schema.main_chart import MainChartRequestSchema
from repository.day_price import DayPriceData


router = APIRouter(prefix='/modelsprices', tags=['ModelsPrices'])


@router.post('/modelspriceschart/', status_code=status.HTTP_200_OK)
async def models_prices_chart(
    chart: MainChartRequestSchema,
    session=Depends(get_session)
):
    try:
        shops = None
        brands = None
        os = None
        screen_resolutions = None
        matrix_types = None
        refresh_rate = None
        currency = None
        diag_min = None
        diag_max = None
        tv_ids = None
        for item in chart.root:
            if item.field == "date_range":
                date_start = item.data.start
                date_end = item.data.end
            elif item.field == "diagonal":
                diag_min = item.data.min
                diag_max = item.data.max
            elif item.field == 'shops':
                shops = item.data
            elif item.field == 'brands':
                brands = item.data
            elif item.field == 'os':
                os = item.data
            elif item.field == 'screen_resolutions':
                screen_resolutions = item.data
            elif item.field == 'matrix_types':
                matrix_types = item.data
            elif item.field == 'refresh_rate':
                refresh_rate = item.data
            elif item.field == 'currency':
                currency = item.data
            elif item.field == 'tv_ids':
                tv_ids = item.data

        results = await DayPriceData(session=session).get_models_prices(
            date_start=date_start,
            date_end=date_end,
            diag_min=diag_min,
            diag_max=diag_max,
            shops=shops,
            brands=brands,
            os=os,
            screen_resolutions=screen_resolutions,
            matrix_type=matrix_types,
            refresh_rate=refresh_rate,
            tv_ids=tv_ids,
            currency=currency
        )
        res_dict = {}
        for i in results:
            if not res_dict.get(i[2], None):
                res_dict[i[2]] = []
            buf_list = [i[1], i[0]]
            res_dict[i[2]].append(buf_list)
        res = []
        for key, value in res_dict.items():
            res.append({
                'name': key,
                'coords': value
            })
        return res

    except MyHttpException:
        raise
    except Exception as e:
        raise MyHttpException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
            title='Ошибка backend'
        )


@router.post('/modelspricesfile/', status_code=status.HTTP_200_OK)
async def models_prices_file(
    chart: MainChartRequestSchema,
    session=Depends(get_session)
):
    try:
        shops = None
        brands = None
        os = None
        screen_resolutions = None
        matrix_types = None
        refresh_rate = None
        currency = None
        diag_min = None
        diag_max = None
        tv_ids = None
        for item in chart.root:
            if item.field == "date_range":
                date_start = item.data.start
                date_end = item.data.end
            elif item.field == "diagonal":
                diag_min = item.data.min
                diag_max = item.data.max
            elif item.field == 'shops':
                shops = item.data
            elif item.field == 'brands':
                brands = item.data
            elif item.field == 'os':
                os = item.data
            elif item.field == 'screen_resolutions':
                screen_resolutions = item.data
            elif item.field == 'matrix_types':
                matrix_types = item.data
            elif item.field == 'refresh_rate':
                refresh_rate = item.data
            elif item.field == 'currency':
                currency = item.data
            elif item.field == 'tv_ids':
                tv_ids = item.data

        results = await DayPriceData(session=session).get_models_prices(
            date_start=date_start,
            date_end=date_end,
            diag_min=diag_min,
            diag_max=diag_max,
            shops=shops,
            brands=brands,
            os=os,
            screen_resolutions=screen_resolutions,
            matrix_type=matrix_types,
            refresh_rate=refresh_rate,
            tv_ids=tv_ids,
            currency=currency
        )
        date_set = set()
        name_prise_dict = {}
        for i in results:
            date_set.add(i[1])
            if not name_prise_dict.get(i[2], None):
                name_prise_dict[i[2]] = {}
            name_prise_dict[i[2]][i[1]] = i[0]
        list_sort_date = sorted(list(date_set))
        fieldnames = ['Name'] + list_sort_date

        data_to_export = []
        for key, values in name_prise_dict.items():
            name = key.replace(';', ' ').replace(',', ' ')
            data_to_export.append({
                'Name': name,
                **values
            })

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        writer.writerows(data_to_export)
        output.seek(0)
        csv_string = output.getvalue()
        output.close()

        bom = '\ufeff'
        content = (bom + csv_string).encode('utf-8-sig')
        return Response(
            content=content,
            media_type="text/csv; charset=utf-8-sig",
            headers={"Content-Disposition": "attachment; filename=generated_data.csv"}
        )

    except MyHttpException:
        raise
    except Exception as e:
        raise MyHttpException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
            title='Ошибка backend'
        )
