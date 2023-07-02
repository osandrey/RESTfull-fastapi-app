import redis.asyncio as async_redis
import re
from typing import Callable
from ipaddress import ip_address

from fastapi_limiter import FastAPILimiter
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.conf.config import settings
from src.routes import contacts, auth
from src.repository.users import get_user_by_bunned_field

app = FastAPI(title="OSA-SWAGGER", swagger_ui_parameters={"operationsSorter": "method"})
user_agent_ban_list = [r"Python-urllib"]
BUNNED_IPS = [ip_address(x.ip) for x in get_user_by_bunned_field() if get_user_by_bunned_field()]
print(f'BaNNED_IPS: {BUNNED_IPS}')
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
    user_agent = request.headers.get("user-agent")
    for ban_pattern in user_agent_ban_list:
        if re.search(ban_pattern, user_agent):
            return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": "You are banned"})
    response = await call_next(request)
    return response


@app.middleware("http")
async def limit_access_by_ip(request: Request, call_next: Callable):
    ip = ip_address(request.client.host)
    if ip in BUNNED_IPS:
        print(f'I am in BANNED LIST {ip}')
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": "Not allowed IP address"})
    response = await call_next(request)
    return response


@app.on_event("startup")
async def startup():
    r = await async_redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0, encoding="utf-8",
                          decode_responses=True)
    await FastAPILimiter.init(r)


@app.post("/reset-password")
async def reset_password(email: str):
    
    return {"message": "Password reset request received"}


@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Hello World"}

