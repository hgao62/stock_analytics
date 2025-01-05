"""Module to store firebase table(collections) names and Alembic data models."""
from sqlalchemy import Column, Integer, String, Float, Date, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = MetaData()

class TableList:
    INDEX_PRICE = 'INDEX_PRICE'
    NASDAQ_HOLDINGS = 'NASDAQ_HOLDINGS'
    SP500_HOLDINGS = 'SP500_HOLDINGS'
    SP500_SECTOR_INFO = 'SP500_SECTOR_INFO'
    SP500_STOCKS_PRICE = 'SP500_STOCKS_PRICE'

class IndexPrice(Base):
    __tablename__ = TableList.INDEX_PRICE
    Date = Column(Date, primary_key=True)
    Ticker = Column(String, primary_key=True)
    Close = Column(Float)

class NASDAQHoldings(Base):
    __tablename__ = TableList.NASDAQ_HOLDINGS
    Ticker = Column(String, primary_key=True)
    Sector = Column(String)
    Industry = Column(String)
    CompanyName = Column(String)


class SP500Holdings(Base):
    __tablename__ = TableList.SP500_HOLDINGS
    Ticker = Column(String, primary_key=True)
    Sector = Column(String)
    Industry = Column(String)
    CompanyName = Column(String)

class SP500StocksPrice(Base):
    __tablename__ = TableList.SP500_STOCKS_PRICE
    Ticker = Column(String, primary_key=True)
    Date = Column(Date, primary_key=True)
    Close = Column(Float)
    Volume = Column(Integer)
    StockSplits = Column(Integer)