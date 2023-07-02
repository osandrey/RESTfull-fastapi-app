# hw_11_fastapi

docker run --name my_hw_postgres_container -e POSTGRES_PASSWORD=567234 -e POSTGRES_DB=hw_app -p 5432:5432 -d postgres

uvicorn start server: ```uvicorn main:app --host localhost --port 8000 --reload```


ALEMBIC MIGRATIONS:
alembic revision --autogenerate -m 'add auth4'
alembic upgrade head 


Passes`:
andrii@google.com
andrii123

"access_token": ```eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJvc2FuZHJleW1hbkBnbWFpbC5jb20iLCJpYXQiOjE2ODgyMjQ3NzMsImV4cCI6MTY4ODIyNTY3Mywic2NvcGUiOiJhY2Nlc3NfdG9rZW4ifQ.ulSqsVbXd8e3G8hCq_vWrlMw1ybMkLjSERu1nExiDZc```