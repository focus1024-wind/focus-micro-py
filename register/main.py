import asyncio
import time
from typing import Dict, Set

from fastapi import FastAPI

from common.model import ServiceInfo, MicroJsonResponse
from register.config import KEEPALIVE_TIME, KEEPALIVE_NUM, SERVER_HOST, SERVER_PORT

app = FastAPI()

register_services: Dict[str, Set[ServiceInfo]] = {}


@app.post("/register")
async def register(service: ServiceInfo):
    """
    服务注册
    :param service:
    :return:
    """
    print(service.name)
    service.register_time = time.time()
    service.keepalive_time = time.time()
    if service.name in register_services:
        # 服务实例已存在
        for register_service in register_services[service.name]:
            if register_service == service:
                register_service.keepalive_time = service.keepalive_time
                break
        else:
            register_services[service.name].add(service)
    else:
        register_services[service.name] = {service}

    return MicroJsonResponse.success(register_services)


@app.get("/service/{service_name}")
async def get_service(service_name: str):
    """
    获取指定服务的可用实例列表
    :param service_name:
    :return:
    """
    return MicroJsonResponse.success(register_services[service_name])


@app.get("/services")
async def get_services():
    """
    获取全部服务
    :return:
    """
    return MicroJsonResponse.success(register_services)


async def keepalive():
    """
    心跳检测
    """
    while True:
        current_time = time.time()
        for services in register_services.values():
            # Python 不允许在迭代的过程中修改集合
            # 收集需要删除的对象信息，在迭代外进行集合修改
            to_remove = {service for service in services if
                         current_time - service.keepalive_time > KEEPALIVE_TIME * KEEPALIVE_NUM}
            services -= to_remove
        await asyncio.sleep(KEEPALIVE_TIME)


async def startup_event():
    """
    fastapi 启动事件
    注册定时服务
    :return:
    """
    asyncio.create_task(keepalive())


if __name__ == '__main__':
    app.add_event_handler("startup", startup_event)

    import uvicorn

    uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT)
