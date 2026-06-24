from datetime import date as datetype

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased
from sqlalchemy import select

from model.exchange_rate import ExchangeRate
from repository.currency import CurrencyData
from model.currency import Currency
from repository.base import BaseData


class ExchangeRateData(BaseData):
    def __init__(self, session: AsyncSession):
        super().__init__(model=ExchangeRate, session=session)

    async def check_exist(self, date: datetype, currency_id: int = None) -> bool:
        if currency_id:
            query = select(select(ExchangeRate).where(
                (ExchangeRate.currency_id == currency_id) &
                (ExchangeRate.date == date)
            ).exists())
        else:
            query = select(select(ExchangeRate).where(
                ExchangeRate.date == date
            ).exists())
        is_exist = await self.session.scalar(query)
        return is_exist

    async def get_chart_period(self, date_start: datetype, date_end: datetype):
        bel_currency = await CurrencyData(self.session).get_by_name('BYN')
        currency_alias = aliased(Currency)
        base_currency_alias = aliased(Currency)
        query = select(
            ExchangeRate.date,
            ExchangeRate.scale,
            ExchangeRate.rate,
            currency_alias.name
        ).join(
            base_currency_alias, ExchangeRate.base_currency
        ).join(
            currency_alias, ExchangeRate.currency
        ).where(
            (ExchangeRate.date >= date_start) &
            (ExchangeRate.date <= date_end),
            ExchangeRate.base_currency_id == bel_currency.id
        ).order_by(
            ExchangeRate.date
        )
        buf_rez = await self.session.execute(query)
        rez = buf_rez.all()

        buf_dict = {}
        for i in rez:
            if buf_dict.get(i[3]) is None:
                buf_dict[i[3]] = {
                    "name": i[3],
                    "coords": list()
                    }
            buf_dict[i[3]]["coords"].append(
                [
                    i[0].strftime('%Y-%m-%d'),
                    float(i[2]),
                    i[1],
                ])

        rez_list = []
        for _, value in buf_dict.items():
            rez_list.append(value)
        return rez_list
