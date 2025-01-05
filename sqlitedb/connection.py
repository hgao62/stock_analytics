from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlitedb.models import Base

DATABASE_PATH = r"C:\development\repo\stock_analytics\sqlitedb\stock_analytics.db"

# Create a SQLAlchemy engine for Alembic
ENGINE = create_engine(f'sqlite:///{DATABASE_PATH}')
Session = sessionmaker(bind=ENGINE)

def main():
    # Perform database operations here
    pass

if __name__ == "__main__":
    main()
