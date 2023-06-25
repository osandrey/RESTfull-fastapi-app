# hw_11_fastapi

docker run --name my_hw_postgres_container -e POSTGRES_PASSWORD=567234 -e POSTGRES_DB=hw_app -p 5432:5432 -d postgres

uvicorn start server: uvicorn main:app --host localhost --port 8000 --reload


ALEMBIC MIGRATIONS:
alembic revision --autogenerate -m 'add auth4'
alembic upgrade head 

Passes`:
andrii@google.com
andrii123
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhbmRyaWlAZ29vZ2xlLmNvbSIsImlhdCI6MTY4NzY5OTc2NywiZXhwIjoxNjg3NzAwNjY3LCJzY29wZSI6ImFjY2Vzc190b2tlbiJ9.Z9PzYgbFRCaxoiqF_Y8dq_U3VsHxt5JkSonFSWzJg-E