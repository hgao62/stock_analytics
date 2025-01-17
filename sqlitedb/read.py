import pandas as pd
from sqlitedb.connection import ENGINE, Session
from sqlitedb.models import SP500StocksPrice, Users
from typing import Dict, Tuple, Optional, List

def read_data_from_sqlite(model, filters: Dict[str, any] = None, date_range: Tuple[str, str] = None, columns_to_select: Optional[List[str]] = None, is_distinct: Optional[bool] = None) -> pd.DataFrame:
    """
    Read data from a SQLite table using ORM model with optional filters and date range.
    
    Parameters:
        model: SQLAlchemy ORM model.
        filters (Dict[str, any]): Dictionary of column-value pairs for filtering.
        date_range (Tuple[str, str]): Tuple containing the start and end dates for filtering.
        columns_to_select (Optional[List[str]]): List of columns to select.
        is_distinct (Optional[bool]): Whether to select distinct rows.
    
    Returns:
        pd.DataFrame: DataFrame containing the query results.
    """
    session = Session()
    try:
        query = session.query(model)
   
        if columns_to_select:
            query = query.with_entities(*[getattr(model, col) for col in columns_to_select])
        # else:
        #     query = query.with_entities(*[getattr(model, col) for col in model.__table__.columns.keys()])
        
        if is_distinct:
            query = query.distinct()
            
        if date_range:
            start_date, end_date = date_range
            query = query.filter(model.Date.between(start_date, end_date))
        
        if filters:
            for column, value in filters.items():
                query = query.filter(getattr(model, column) == value)
        
        results = query.all()
        
        if columns_to_select:
            df = pd.DataFrame(results, columns=columns_to_select)
        else:
            df = pd.DataFrame([item.__dict__ for item in results])
        # df = pd.DataFrame(results, columns=columns_to_select)
        if '_sa_instance_state' in df.columns:
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

def read_from_user():
    df = read_data_from_sqlite(Users)
    print(df.head())

if __name__ == "__main__":
    read_from_user()
    main()
