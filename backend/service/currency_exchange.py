from typing import Optional, List
from datetime import date as datetype
from decimal import Decimal
import decimal

from model.currency import Currency
from repository.currency import CurrencyData
from repository.exchange_rate import ExchangeRateData


async def currency_exchange(
        session,
        from_cur: Currency,
        to_cur: Currency,
        price: int,
        date: datetype,
        cur_bel: Optional[Currency] = None,
        exchange_range_list: Optional[List[Currency]] = None):
    try:
        if from_cur == to_cur:
            return price
        if not from_cur or not to_cur or not price or not date:
            print(from_cur, to_cur, date)
            raise Exception('not all params')
        if not cur_bel:
            cur_bel = await CurrencyData(session).get_by_name('BYN')
        exchange_range = None
        if not exchange_range_list:
            exchange_range = await ExchangeRateData(session).get_by_cur_date(from_cur, date)
            if not exchange_range or exchange_range == 1:
                buf_price = 1
            else:
                buf_price = Decimal(price) * exchange_range.rate / exchange_range.scale
            exchange_range = await ExchangeRateData(session).get_by_cur_date(to_cur, date)
            if not exchange_range or exchange_range == 1:
                return buf_price.quantize(Decimal('1.00'), rounding=decimal.ROUND_HALF_UP)
            else:
                buf_price = Decimal(buf_price) * exchange_range.rate / exchange_range.scale
            return buf_price.quantize(Decimal('1.00'), rounding=decimal.ROUND_HALF_UP)
        else:
            exchange_from = None
            exchange_to = None
            for i in exchange_range_list:
                if i.currency_id == from_cur.id and i.date == date:
                    exchange_from = i
                if i.currency_id == to_cur.id and i.date == date:
                    exchange_to = i
                if exchange_from and exchange_to:
                    break

            if not exchange_from:
                exchange_from = await ExchangeRateData(session).get_by_cur_date(from_cur, date)
                if exchange_from and exchange_from != -1:
                    exchange_range_list.append(exchange_from)
            if not exchange_to:
                exchange_to = await ExchangeRateData(session).get_by_cur_date(to_cur, date)
                if exchange_to and exchange_to != -1:
                    exchange_range_list.append(exchange_to)

            buf_price = Decimal(price)
            if exchange_from:
                buf_price = Decimal(price) * exchange_from.rate / exchange_from.scale
            if exchange_to:
                buf_price = Decimal(buf_price) * exchange_to.rate / exchange_to.scale
            return buf_price.quantize(Decimal('1.00'), rounding=decimal.ROUND_HALF_UP)

    except Exception:
        raise
