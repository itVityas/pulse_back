import requests
from datetime import date as datetype
import datetime

from repository.currency import CurrencyData
from model.exchange_rate import ExchangeRate
from repository.exchange_rate import ExchangeRateData


nbrb_url = 'https://api.nbrb.by/exrates/rates'
nbrb_period_url = 'https://api.nbrb.by/exrates/rates/dynamics/'


async def get_currency_from_nbrb(session, date: datetype):
    """
    Get currency data from nbrb
    :param currency_id: currency id
    :param date: date
    :return: currency data
    """
    try:
        if await ExchangeRateData(session).check_exist(date=date):
            return
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


async def get_currency_period_from_nbrb(session, date_start: datetype, date_end: datetype):
    try:
        bel_currency = await CurrencyData(session).get_by_name('BYN')
        currensies, _ = await CurrencyData(session).get_multi()
        for currency in currensies:
            if currency.name == 'BYN':
                continue
            json_data = requests.get(
                nbrb_period_url + f'{currency.cur_id}?startDate={date_start}&endDate={date_end}'
            ).json()
            if json_data:
                for line in json_data:
                    date_line = datetime.datetime.strptime(line.get('Date'), '%Y-%m-%dT%H:%M:%S').date()
                    if await ExchangeRateData(session).check_exist(date=date_line, currency_id=currency.id):
                        continue
                    rate = float(line.get('Cur_OfficialRate'))
                    scale = 1
                    if currency.name == 'RUB':
                        scale = 100
                    if currency.name == 'CNY':
                        scale = 10
                    if rate:
                        exc_rate = ExchangeRate(
                            currency_id=currency.id,
                            date=date_line,
                            rate=rate,
                            scale=scale,
                            base_currency_id=bel_currency.id
                        )
                        await ExchangeRateData(session).create_by_model(exc_rate)

    except Exception as ex:
        raise ex
