import inspect
import json

import requests

from calc_server.config import REGISTER_CENTER
from common.model import register_services, ServiceInfo


class MicroRequestError(Exception):
    def __init__(self, message):
        super(MicroRequestError, self).__init__(message)


class MicroRequest:
    def get(
            self,
            server_name: str,
            path: str = '',
    ):
        def decorator(func):
            def wrapper(*args, **kwargs):
                response = None
                try:
                    url = self.__get_server__(server_name, path)

                    # 获取函数签名
                    sig = inspect.signature(func)
                    # 绑定参数到签名
                    bound_args = sig.bind(*args, **kwargs)
                    # 获取返回类型
                    return_type = sig.return_annotation

                    params = "?"
                    for name, value in bound_args.arguments.items():
                        if url.find(f'{{{name}}}'):
                            url = url.replace(f'{{{name}}}', str(value))
                        else:
                            params = f'{params}{name}={value}&'
                    params = params[:-1]

                    response = requests.request("GET", f'{url}{params}')
                    if response.status_code != 200:
                        raise MicroRequestError(response.json())
                    else:
                        return return_type.model_validate(response.json())
                except AttributeError:
                    if response is not None:
                        return response.json()
                    else:
                        raise MicroRequestError(AttributeError)

            return wrapper

        return decorator

    def post(
            self,
            server_name: str,
            path: str = '',
    ):
        def decorator(func):
            def wrapper(*args, **kwargs):
                url = self.__get_server__(server_name, path)

                # 获取函数签名
                sig = inspect.signature(func)

                # 获取返回类型
                return_type = sig.return_annotation

                for arg in args:
                    payload = json.dumps(arg.__dict__)
                    response = requests.request("POST", url, data=payload)
                    if response.status_code != 200:
                        raise MicroRequestError(response.text)
                    else:
                        return return_type.model_validate(response.json())
                else:
                    response = requests.request("POST", url)
                    if response.status_code != 200:
                        raise MicroRequestError(response.text)
                    else:
                        return return_type.model_validate(response.json())

            return wrapper

        return decorator

    def __get_server__(self, server_name, path) -> str:
        if server_name == 'REGISTER_CENTER':
            # 服务注册
            if path[0] == '/':
                return f"{REGISTER_CENTER}{path}"
            else:
                return f"{REGISTER_CENTER}/{path}"
        else:
            # 服务调用
            # 获取对应服务
            servers = register_services.get(server_name)
            if servers is None:
                raise MicroRequestError(f'{server_name} is not exist')

            # ToDo: 服务负载均衡
            for server in servers:
                server_obj = ServiceInfo.model_validate(server)
                if path[0] == '/':
                    return f"{server_obj.service}{path}"
                else:
                    return f"{server_obj.service}/{path}"
