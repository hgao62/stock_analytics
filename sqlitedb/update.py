from alembic import op
import sqlalchemy as sa
from sqlitedb.connection import ENGINE, Session
from sqlitedb.models import SP500StocksPrice

def update_data_in_sqlite(model, set_values: dict, filters: dict=None, date_range: tuple = None) -> None:
    """
    Update data in a SQLite table using ORM model.
    
    Parameters:
        model: SQLAlchemy ORM model.
        set_values (dict): Dictionary of column-value pairs to set.
        where_clause (dict): Dictionary of column-value pairs for the WHERE clause.
        date_range (tuple): Tuple containing the start and end dates for filtering.
    """
    if not filters and not date_range:
        raise ValueError("A WHERE clause or date range must be provided to update data.")

    session = Session()
    try:
        query = session.query(model)
        if date_range:
            start_date, end_date = date_range
            query = query.filter(model.Date.between(start_date, end_date))
        
        if filters:
            for column, value in filters.items():
                query = query.filter(getattr(model, column) == value)
        
        query.update(set_values)
        session.commit()
        print(f"Data updated in table {model.__tablename__} successfully.")
    except Exception as e:
        print(f"Error updating data in SQLite table {model.__tablename__}: {e}")
    finally:
        session.close()

def main():
    set_values = {"Close": 155.0}
    where_clause = {"Ticker": 'AAPL'}
    date_range = ('2023-10-01', '2023-10-31')
    update_data_in_sqlite(SP500StocksPrice, set_values, where_clause, date_range)

if __name__ == "__main__":
    main()
