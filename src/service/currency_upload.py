import requests
from datetime import date as datetype

from repository.currency import CurrencyData
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
        for line in json_data:
            name = line.get('Cur_Abbreviation')
            if name:
                currency = await CurrencyData(session).get_by_name(name=name)
                if currency:
                    print(currency, line)

    except Exception as ex:
        raise ex
