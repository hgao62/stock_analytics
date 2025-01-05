import pandas as pd
from sqlitedb.connection import ENGINE, Session
from sqlitedb.models import SP500StocksPrice
from typing import Dict, Tuple

def read_data_from_sqlite(model, filters: Dict[str, any] = None, date_range: Tuple[str, str] = None) -> pd.DataFrame:
    """
    Read data from a SQLite table using ORM model with optional filters and date range.
    
    Parameters:
        model: SQLAlchemy ORM model.
        filters (Dict[str, any]): Dictionary of column-value pairs for filtering.
        date_range (Tuple[str, str]): Tuple containing the start and end dates for filtering.
    
    Returns:
        pd.DataFrame: DataFrame containing the query results.
    """
    session = Session()
    try:
        query = session.query(model)
        if date_range:
            start_date, end_date = date_range
            query = query.filter(model.Date.between(start_date, end_date))
        
        if filters:
            for column, value in filters.items():
                query = query.filter(getattr(model, column) == value)
        
        results = query.all()
        df = pd.DataFrame([item.__dict__ for item in results])
        if not df.empty:
            df.drop('_sa_instance_state', axis=1, inplace=True)
        print(f"Data read from SQLite successfully.")
        
    except Exception as e:
        print(f"Error reading data from SQLite: {e}")
        raise e
    finally:
        session.close()
    
    return df

def main():
    filters = {"Ticker": 'AAPL'}
    date_range = ('2023-10-01', '2023-10-31')
    df = read_data_from_sqlite(SP500StocksPrice, filters, date_range)
    print(df.head())

if __name__ == "__main__":
    main()
