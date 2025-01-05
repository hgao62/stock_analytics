"""Module to store firebase table(collections) names and Alembic data models."""
from sqlalchemy import Column, Integer, String, Float, Date, MetaData, Table, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()
metadata = MetaData()

class TableList:
    INDEX_PRICE = 'INDEX_PRICE'
    NASDAQ_HOLDINGS = 'NASDAQ_HOLDINGS'
    SP500_HOLDINGS = 'SP500_HOLDINGS'
    SP500_SECTOR_INFO = 'SP500_SECTOR_INFO'
    SP500_STOCKS_PRICE = 'SP500_STOCKS_PRICE'
    STOCKS_PRICE = 'STOCKS_PRICE'
# Association table for the many-to-many relationship
watchlist_association = Table(
    'watchlist_association', Base.metadata,
    Column('user_id', String, ForeignKey('Users.User')),
    Column('ticker_id', String, ForeignKey('WatchListTickers.Ticker'))
)

class IndexPrice(Base):
    __tablename__ = TableList.INDEX_PRICE
    Date = Column(Date, primary_key=True)
    Ticker = Column(String, primary_key=True)
    Close = Column(Float)
    Name = Column(String)

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
    
class StocksPrice(Base):
    __tablename__ = TableList.STOCKS_PRICE
    Ticker = Column(String, primary_key=True)
    Date = Column(Date, primary_key=True)
    Close = Column(Float)
    Volume = Column(Integer)
    StockSplits = Column(Integer)
    IndexName = Column(String)
    

class WatchListTickers(Base):
    __tablename__ = 'WatchListTickers'
    Ticker = Column(String, primary_key=True)
    users = relationship('Users', secondary=watchlist_association, back_populates='watchlist_tickers')

class Users(Base):
    __tablename__ = 'Users'
    User = Column(String, primary_key=True)
    Password = Column(String)
    Email = Column(String)
    FirstName = Column(String)
    LastName = Column(String)
    Phone = Column(String)
    Address = Column(String)
    City = Column(String)
    State = Column(String)
    Zip = Column(String)
    Country = Column(String)
    Role = Column(String)
    Active = Column(Integer)
    Created = Column(Date)
    Updated = Column(Date)
    watchlist_tickers = relationship('WatchListTickers', secondary=watchlist_association, back_populates='users')