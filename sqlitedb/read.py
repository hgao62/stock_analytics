from sqlalchemy.orm import Session
import pandas as pd
from sqlitedb.connection import ENGINE, Session
from sqlitedb.models import SP500StocksPrice
from typing import Dict

def read_data_from_sqlite(model, filters: Dict[str, any] = None) -> pd.DataFrame:
    """
    Read data from a SQLite table using ORM model with optional filters.
    
    Parameters:
        model: SQLAlchemy ORM model.
        filters (Dict[str, any]): Dictionary of column-value pairs for filtering.
    
    Returns:
        pd.DataFrame: DataFrame containing the query results.
    """
    session = Session()
    try:
        query = session.query(model)
        if filters:
            for column, value in filters.items():
                query = query.filter(getattr(model, column) == value)
        results = query.all()
        df = pd.DataFrame([item.__dict__ for item in results])
        df.drop('_sa_instance_state', axis=1, inplace=True)
        print(f"Data read from SQLite successfully.")
        return df
    except Exception as e:
        print(f"Error reading data from SQLite: {e}")
        return pd.DataFrame()
    finally:
        session.close()

def main():
    filters = {"Ticker": 'AAPL'}
    df = read_data_from_sqlite(SP500StocksPrice, filters)
    print(df.head())

if __name__ == "__main__":
    main()
