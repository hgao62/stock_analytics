from sqlalchemy.orm import Session
import pandas as pd
from sqlitedb.connection import ENGINE, Session
from sqlitedb.models import SP500StocksPrice
from sqlitedb.delete import truncate_table

def write_data_to_sqlite(model, data: pd.DataFrame,clear_existing_data=False) -> None:
    """
    Write data to a SQLite table using ORM model.
    
    Parameters:
        model: SQLAlchemy ORM model.
        data (pd.DataFrame): DataFrame containing the data to write.
    """
    session = Session()
    try:
        if clear_existing_data:
           truncate_table(model)
        records = data.to_dict(orient='records')
        session.bulk_insert_mappings(model, records)
        session.commit()
        print(f"Data written to table {model.__tablename__} successfully.")
    except Exception as e:
        print(f"Error writing data to SQLite table {model.__tablename__}: {e}")
    finally:
        session.close()

def main():
    # Example DataFrame
    data = pd.DataFrame({
        'Ticker': ['AAPL', 'MSFT'],
        'Date': ['2023-10-01', '2023-10-01'],
        'Close': [150.0, 250.0]
    })
    
    write_data_to_sqlite(SP500StocksPrice, data)

if __name__ == "__main__":
    main()
