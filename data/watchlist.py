from sqlalchemy.orm import Session
from sqlitedb.connection import ENGINE, Session
from sqlitedb.models import Users, WatchListTickers
import pandas as pd
import logging

def load_tickers():
    ticker_df = pd.read_csv('./reports/kobe_watch_list.csv')
    tickers = ticker_df['Ticker'].tolist()
    return tickers
def add_tickers(tickers):
    session = Session()
    user = Users(User='kobegao', Email='hgao62@uwo.ca', FirstName='kobe', LastName='gao')
    for ticker in tickers:
        ticker_obj = WatchListTickers(Ticker=ticker)
        user.watchlist_tickers.append(ticker_obj)
        session.add(ticker_obj)
    session.commit()
    session.close()
    
def daily_tickers_update(user, tickers_to_add):
    session = Session()
    user = session.query(Users).filter_by(User=user).first()
    new_tickers = []
    existing_tickers = [ticker.Ticker for ticker in user.watchlist_tickers]
    for ticker in tickers_to_add:
        if ticker not in existing_tickers:
            ticker_obj = WatchListTickers(Ticker=ticker)
            user.watchlist_tickers.append(ticker_obj)
            session.add(ticker_obj)
            new_tickers.append(ticker)
    session.commit()
    session.close()
    logging.info(f"Added {new_tickers} to {user}'s watchlist.")
    
def read_user_tickers(user):
    session = Session()
    user = session.query(Users).filter_by(User=user).first()
    user_tickers = [ticker.Ticker for ticker in user.watchlist_tickers]
    session.close()
    logging.info(f"Loaded {user}'s watchlist: {user_tickers}")
    return user_tickers
    
def get_user_tickers(user):
    new_tickers = load_tickers()
    daily_tickers_update(user, new_tickers)
    final_user_tickers = read_user_tickers(user)
    return final_user_tickers
    
def main(mode):
    tickers = load_tickers()
    if mode =='initial':
        add_tickers(tickers)
    elif mode == 'daily':
        daily_tickers_update('kobegao',tickers)

if __name__ == "__main__":
    res = get_user_tickers('kobegao')
    print(res)