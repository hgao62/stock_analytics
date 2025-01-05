from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlitedb.connection import Session

# Define the base class for the ORM models
Base = declarative_base()

# Define a sample ORM model
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)


def truncate_table(model):
    session = Session()
    try:
        # Truncate the table
        session.query(model).delete()
        # Commit the transaction
        session.commit()
        print(f"Table {model.__tablename__} truncated successfully.")
    except Exception as e:
        session.rollback()
        print(f"Error truncating table {model.__tablename__}: {e}")
    finally:
        session.close()
    
# Function to delete data from the table
def delete_user(user_id):
    try:
        # Query the user by id
        user = session.query(User).filter(User.id == user_id).one()
        # Delete the user
        session.delete(user)
        # Commit the transaction
        session.commit()
        print(f"User with id {user_id} deleted successfully.")
    except Exception as e:
        session.rollback()
        print(f"Error deleting user: {e}")
    finally:
        session.close()

# Example usage
if __name__ == "__main__":
    # Delete user with id 1
    delete_user(1)
    # Function to delete all data from the table
    def delete_all_users():
        try:
            # Delete all rows in the users table
            num_rows_deleted = session.query(User).delete()
            # Commit the transaction
            session.commit()
            print(f"All users deleted successfully. Number of rows deleted: {num_rows_deleted}")
        except Exception as e:
            session.rollback()
            print(f"Error deleting all users: {e}")
        finally:
            session.close()
