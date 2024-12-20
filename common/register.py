import asyncio

from common.model import MicroJsonResponse, ServiceInfo, register_services
from common.request import MicroRequest

request = MicroRequest()


@request.post(server_name="REGISTER_CENTER", path='/register')
def register_client(service: ServiceInfo) -> MicroJsonResponse:
    pass


async def register_task(server_name, server, keepalive_time: int = 60):
    while True:
        register_services.clear()
        register_services.update(register_client(ServiceInfo(name=server_name, service=server)).data)
        await asyncio.sleep(keepalive_time)
