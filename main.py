from typing import Union
from fastapi import FastAPI, HTTPException
from sqlmodel import Field, Session, SQLModel, create_engine, select

app = FastAPI()

db_name = 'fast_api_demo_db'
username = 'admin'
password = 'Admin123'
host = '127.0.0.1'
DATABASE_URL = f"mysql+pymysql://{username}:{password}@{host}/{db_name}"

# Create a SQLModel engine
engine = create_engine(DATABASE_URL, echo=True)


# Define the User model
class User(SQLModel, table=True):
    __tablename__ = "user_info"
    user_id: int = Field(primary_key=True, index=True)
    firstname: str = Field(index=True)  # Add index=True
    surname: str = Field(index=True)


# Ensure the database and tables are created
SQLModel.metadata.create_all(engine)


@app.get("/users/{firstname}/{surname}")
async def get_user_by_name(firstname: str, surname: str):
    try:
        with Session(engine) as session:
            statement = select(User).where(User.firstname == firstname, User.surname == surname)
            print(f"Executing SQL: {statement}")
            results = session.exec(statement).all()
            print(f"Query Results: {results}")

            if not results:
                raise HTTPException(status_code=404, detail="User not found")

            users = [
                {"user_id": user.user_id, "firstname": user.firstname, "surname": user.surname} for user in results
            ]
            return {"users": users}

    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.post("/users/")
async def add_user(firstname: str, surname: str):
    """
    Add a new user to the database.
    """
    try:
        with Session(engine) as session:
            new_user = User(firstname=firstname, surname=surname)
            session.add(new_user)
            session.commit()
            session.refresh(new_user)
            return {"message": "User added successfully",
                    "user": {"user_id": new_user.user_id, "firstname": new_user.firstname, "surname": new_user.surname}}

    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get('/hello')
async def hello_world():
    return {"message": "Hello, World!"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
