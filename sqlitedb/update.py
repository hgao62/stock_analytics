from alembic import op
import sqlalchemy as sa
from sqlitedb.connection import ENGINE, Session
from sqlitedb.models import SP500StocksPrice

def upsert_data_in_sqlite(model, set_values: dict, filters: dict=None, date_range: tuple = None) -> None:
    """
    Upsert data in a SQLite table using ORM model.
    
    Parameters:
        model: SQLAlchemy ORM model.
        set_values (dict): Dictionary of column-value pairs to set.
        filters (dict): Dictionary of column-value pairs for the WHERE clause.
        date_range (tuple): Tuple containing the start and end dates for filtering.
    """
    if not filters and not date_range:
        raise ValueError("A WHERE clause or date range must be provided to upsert data.")

    session = Session()
    try:
        query = session.query(model)
        if date_range:
            start_date, end_date = date_range
            query = query.filter(model.Date.between(start_date, end_date))
        
        if filters:
            for column, value in filters.items():
                query = query.filter(getattr(model, column) == value)
        
        existing_record = query.first()
        if existing_record:
            query.update(set_values)
            print(f"Data updated in table {model.__tablename__} successfully.")
        else:
            new_record = model(**set_values)
            session.add(new_record)
            print(f"Data inserted into table {model.__tablename__} successfully.")
        
        session.commit()
    except Exception as e:
        print(f"Error upserting data in SQLite table {model.__tablename__}: {e}")
    finally:
        session.close()

def main():
    set_values = {"Ticker": 'AAPL', "Date": '2023-10-15', "Close": 155.0}
    filters = {"Ticker": 'AAPL'}
    date_range = ('2023-10-01', '2023-10-31')
    upsert_data_in_sqlite(SP500StocksPrice, set_values, filters, date_range)

if __name__ == "__main__":
    main()
