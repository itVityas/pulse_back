import requests
from datetime import date as datetype

from repository.currency import CurrencyData
from model.exchange_rate import ExchangeRate
from repository.exchange_rate import ExchangeRateData


nbrb_url = 'https://api.nbrb.by/exrates/rates'


async def get_currency_from_nbrb(session, date: datetype):
    """
    Get currency data from nbrb
    :param currency_id: currency id
    :param date: date
    :return: currency data
    """
    try:
        json_data = requests.get(nbrb_url + f'?{date}' + '&periodicity=0').json()
        cur_bun = await CurrencyData(session).get_by_name(name='BYN')
        count = 0
        for line in json_data:
            name = line.get('Cur_Abbreviation')
            rate = float(line.get('Cur_OfficialRate'))
            if name and rate:
                currency = await CurrencyData(session).get_by_name(name=name)
                if currency:
                    exc_rate = ExchangeRate(
                        currency_id=currency.id,
                        date=date,
                        rate=rate,
                        scale=int(line.get('Cur_Scale')),
                        base_currency_id=cur_bun.id
                    )
                    await ExchangeRateData(session).create_by_model(exc_rate)
                    count += 1

        return count

    except Exception as ex:
        raise ex
