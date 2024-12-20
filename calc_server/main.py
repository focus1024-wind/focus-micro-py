import asyncio
from typing import Union

from fastapi import FastAPI

from calc_server.config import SERVER_HOST, SERVER_PORT, SERVER_NAME, KEEPALIVE_TIME, SERVER
from common.register import register_task

app = FastAPI()


@app.get("/add/{a}/{b}")
async def add(a: Union[int, float], b: Union[int, float]):
    return a + b


@app.get("/subtract/{a}/{b}")
async def subtract(a: Union[int, float], b: Union[int, float]):
    return a - b


@app.get("/multiply/{a}/{b}")
async def multiply(a: Union[int, float], b: Union[int, float]):
    return a * b


@app.get("/divide/{a}/{b}")
async def divide(a: Union[int, float], b: Union[int, float]):
    return a / b


async def startup_event():
    """
    fastapi 启动事件
    注册定时服务
    :return:
    """
    asyncio.create_task(register_task(SERVER_NAME, SERVER, KEEPALIVE_TIME))


if __name__ == '__main__':
    app.add_event_handler("startup", startup_event)

    import uvicorn

    uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT)
