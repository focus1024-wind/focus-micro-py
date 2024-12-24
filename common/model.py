import time
from typing import Self, Dict, Set, Any

from pydantic import BaseModel


class MicroJsonResponse(BaseModel):
    code: int = 200
    message: str = 'OK'
    data: Any = None

    @staticmethod
    def success(data: Any = None) -> dict[str, str | None | int | Any]:
        return {'code': 200, 'message': 'OK', 'data': data}

    @staticmethod
    def error(data: Any = None) -> dict[str, str | None | int | Any]:
        return {'code': 500, 'message': 'error', 'data': data}

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(code={self.code}, message={self.message})'


class ServiceInfo(BaseModel):
    """
    微服务参数信息，用于微服务注册和服务发现
    """

    name: str
    service: str
    register_time: float = time.time()
    keepalive_time: float = time.time()

    def __eq__(self, other: Self) -> bool:
        """
        重写比较方法，用于服务相等判断
        :param other:
        :return:
        """
        return self.name == other.name and self.service == other.service

    def __hash__(self) -> int:
        """
        重写 hash 方法，用于对象相等判断
        :return:
        """
        return hash((self.name, self.service))

    __dict__ = {

    }

register_services: Dict[str, Set[ServiceInfo]] = {}
