import redis.asyncio as async_redis
import re
from typing import Callable
from ipaddress import ip_address

from fastapi_limiter import FastAPILimiter
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.config.config import settings
from src.routes import contacts, auth
from src.repository.users import get_user_by_bunned_field

app = FastAPI(title="OSA-SWAGGER", swagger_ui_parameters={"operationsSorter": "method"})
user_agent_ban_list = [r"Python-urllib"]

app.include_router(auth.router, prefix='/api')
app.include_router(contacts.router, prefix='/api')


origins = [
    "http://localhost:8000"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.middleware("http")
async def user_agent_ban_middleware(request: Request, call_next: Callable):
    """
    The user_agent_ban_middleware function is a middleware function
    that checks the user-agent header of an incoming request.
    If the user-agent matches any of the patterns in our ban list,
    then we return a 403 Forbidden response with a detail message.
    Otherwise, we call next and return whatever response comes back from it.

    :param request: Request: Access the request object
    :param call_next: Callable: Pass the next middleware function in the chain
    :return: A json-response with a status code of 403 and content of {&quot;detail&quot;: &quot;you are banned&quot;}
     if the user-agent header matches any pattern in the user_agent_ban_list
    """
    user_agent = request.headers.get("user-agent")
    for ban_pattern in user_agent_ban_list:
        if re.search(ban_pattern, user_agent):
            return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": "You are banned"})
    response = await call_next(request)
    return response


@app.middleware("http")
async def limit_access_by_ip(request: Request, call_next: Callable):
    """
    The limit_access_by_ip function is a middleware function that limits access to the API by IP address.
    It checks if the client's IP address is in BANNED_IPS, and if so, returns an HTTP 403 Forbidden response.
    Otherwise, it calls call_next() to continue processing.

    :param request: Request: Get the client ip address
    :param call_next: Callable: Pass the next function in the pipeline
    :return: A json-response object
    """
    BUNNED_IPS = [ip_address(x.ip) for x in get_user_by_bunned_field() if get_user_by_bunned_field()]
    try:
        ip = ip_address(request.client.host)
        if ip in BUNNED_IPS:
            print(f'I am in BANNED LIST {ip}')
            return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": "Not allowed IP address"})
    except ValueError as err:
        print(err)
    response = await call_next(request)
    return response


@app.on_event("startup")
async def startup():
    """
    The startup function is called when the application starts up.
    It's a good place to initialize things that are needed by your app, such as database connections or caches.

    :return: A list of objects
    """
    r = await async_redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0, encoding="utf-8",
                          decode_responses=True)
    await FastAPILimiter.init(r)


@app.post("/reset-password")
async def reset_password(email: str):
    """
    The reset_password function takes an email address and sends a password reset link to that email.
        Args:
            email (str): The user's email address.

    :param email: str: Specify the type of data that is expected to be passed into the function
    :return: A dictionary with a message
    """
    return {"message": "Password reset request received"}


@app.get("/", tags=["Root"])
def read_root():
    """
    The read_root function returns a dictionary with the key &quot;message&quot; and value &quot;Hello Kate&quot;.


    :return: A dictionary with a key of message and a value of hello kate
    """
    return {"message": "Hello Kate"}

