from alembic import op
import sqlalchemy as sa
from sqlitedb.connection import ENGINE, Session
from sqlitedb.models import SP500StocksPrice

def update_data_in_sqlite(model, set_values: dict, where_clause: dict) -> None:
    """
    Update data in a SQLite table using ORM model.
    
    Parameters:
        model: SQLAlchemy ORM model.
        set_values (dict): Dictionary of column-value pairs to set.
        where_clause (dict): Dictionary of column-value pairs for the WHERE clause.
    """
    session = Session()
    try:
        query = session.query(model)
        for column, value in where_clause.items():
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
    where_clause = {"Ticker": 'AAPL', "Date": '2023-10-01'}
    update_data_in_sqlite(SP500StocksPrice, set_values, where_clause)

if __name__ == "__main__":
    main()
