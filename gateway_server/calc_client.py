from typing import Union

from common.model import ServiceInfo, register_services
from common.register import register_client
from common.request import MicroRequest

request = MicroRequest()


@request.get(server_name="calc_server", path='/add/{a}/{b}')
def add_client(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    pass


@request.get(server_name="calc_server", path='/subtract/{a}/{b}')
def subtract_client(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    pass


@request.get(server_name="calc_server", path='/multiply/{a}/{b}')
def multiply_client(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    pass


@request.get(server_name="calc_server", path='/divide/{a}/{b}')
def divide_client(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    pass


register_services.clear()
register_services.update(register_client(ServiceInfo(name='1', service='1')).data)


print(add_client(1, 0.5))
