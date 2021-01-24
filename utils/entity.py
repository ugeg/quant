from sqlalchemy import String, Column, Float
from sqlalchemy.dialects.mysql import VARCHAR
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class StockBasic(Base):
    def __repr__(self) -> str:
        return str(self.__dict__)

    __tablename__ = 'stock_basic'
    ts_code = Column(VARCHAR(9,binary=True),primary_key=True)
    # ts_code = Column(String(9), primary_key=True)
    # symbol = Column(String(6))
    symbol = Column(VARCHAR(6,binary=True))
    name = Column(String(10))
    area = Column(String(10))
    industry = Column(String(10))
    fullname = Column(String(100))
    enname = Column(String(100))
    market = Column(String(10))
    exchange = Column(String(10))
    curr_type = Column(String(10))
    list_status = Column(String(1))
    list_date = Column(String(8))
    delist_date = Column(String(8))
    is_hs = Column(String(1))


class Daily(Base):
    def __repr__(self) -> str:
        return str(self.__dict__)

    __tablename__ = 'daily'
    ts_code = Column(String(9), primary_key=True)
    trade_date = Column(String(8), primary_key=True)
    open = Column(Float())
    high = Column(Float())
    low = Column(Float())
    close = Column(Float())
    pre_close = Column(Float())
    change = Column(Float())
    pct_chg = Column(Float())
    vol = Column(Float())
    amount = Column(Float())
