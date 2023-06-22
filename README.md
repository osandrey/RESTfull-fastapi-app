# hw_11_fastapi

docker run --name my_hw_postgres_container -e POSTGRES_PASSWORD=567234 -e POSTGRES_DB=hw_app -p 5432:5432 -d postgres

uvicorn start server: uvicorn main:app --host localhost --port 8000 --reload