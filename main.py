from fastapi import FastAPI

from src.routes import contacts, auth


app = FastAPI(title="OSA-SWAGGER", swagger_ui_parameters={"operationsSorter": "method"})

app.include_router(auth.router, prefix='/api')
app.include_router(contacts.router, prefix='/api')


@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Hello World"}
