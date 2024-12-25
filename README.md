# 项目环境
- Python: 3.12.6

# 项目结构

```
├─calc_server           # 计算服务，负责实现具体的计算功能
│  ├─config.py          # 计算服务配置文件，配置微服务内容和注册中心信息
│  ├─main.py            # 依赖fastapi实现的微服务架构
├─gateway_server        # 网关服务，负责调用计算服务提供的接口，对外提供计算功能
│  ├─calc_client.py     # 通过自定义装配器实现对计算接口的封装
│  ├─config.py          # 网关服务配置文件，配置微服务内容和注册中心信息
│  ├─main.py            # 依赖fastapi实现的微服务架构、
├─common                # 自定义微服务框架封装库
│  ├─model.py           # 对通用模型的封装
│  ├─register.py        # 微服务注册接口封装
│  ├─request.py         # 自定义装配器，实现对其他服务接口的封装，参考 calc_client.py
├─register              # 注册中心
│  ├─config.py          
│  ├─main.py            
```

# 注册中心与服务注册(register)

在微服务架构中，服务之间交互的核心在于知道其他服务的存在和其通讯地址。微服务的服务发现主要有以下方式：

- 注册中心：由一个服务来主要进行服务直接的注册与发现，通过参数配置，所有其他微服务在启动时主动向注册中心发送指令，注册中心收到指令后，管理服务信息。通过心跳机制，定期在注册中心与服务器直接进行心跳通讯，确保服务保活。
- 主机名访问：类似于DNS解析的方式，将主机名翻译为对应的通讯地址进行通讯。适用于同一个网络下、容器化管理、公网域名服务访问等方式。
- 系统配置：直接将其他服务信息配置在配置文件或代码中进行访问。

注册中心是通过单独的服务来管理整个微服务架构下的其他所有服务发现的组件，保存所有微服务间的地址信息，使得各个微服务之间能够找到并进行相互通信。在本框架下，通过自定义注册中心来实现对于其他服务的管理。具体代码参考
`register`文件夹。

本服务所实现的注册中心通过字典集合的方式维护向系统中注册的微服务注册信息，微服务注册后，需要定期向注册中心发送心跳信息，或超过一定时间没有收到对应服务的心跳信息，注册中心会将对应服务从注册列表中删除。

本服务注册中心采用HTTP方式进行通信，并提供如下接口：

- /register [POST]: 服务注册与心跳，返回所有服务注册信息
- /service/{service_name} [GET]: 根据 service_name 服务名查询对应服务列表
- /services [GET]: 获取所有服务注册信息

# 通讯接口封装与客户端接口封装

在服务注册后，已知其他服务名和服务接口的情况下，我们可以通过对应的通讯协议和其他服务接口进行交互。常见的微服务通讯协议有：HTTP、RPC等通讯协议。已知服务通讯信息后，我们可以在代码中通过对应协议向其他服务发起请求，等待响应。但在具体的请求过程中，若将请求代码写死在程序里面，耦合度较高，不利于程序的开发和接口的变更等情况。在具体操作中，可以将请求代码封装以提供接口，
`common`文件夹下通过提供对应封装工具和封装实例以实现其他服务接口的封装。

`common.request.MicroRequest`， 通过Python装饰器特性实现对 requests
库请求HTTP调用的方式进行封装。该装饰器会自动解析方法的签名和返回签名。向指定服务发起请求并获取响应信息。
> - MicroRequest 在对类请求进行序列化的过程中，通过 application/json 格式进行序列化，依赖于类的 __dict__
    方法，若需要对指定类进行序列化定义，可以自定义 __dict__ 方法
> - MicroRequest 在对类响应进行反序列化的过程中，依赖 `pydantic.BaseModel`，可以在自定义类的时候继承 `pydantic.BaseModel`

## 序列化

`__dict__` 是 Python 类的一个特殊的属性，`_dict__` 是一个字典对象，包含了实例的所有可变属性及其对应的值。

```python
class Request:
    name: str
    age: int

    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age


request = Request("focus-micro-py", 1)
print(request.__dict__)

# {'name': 'focus-micro-py', 'age': 1}
```

## 反序列化

pydantic 是一个基于类型注解的数据验证和解析库，通过定义 pydantic模型(BaseModel的子类)来描述数据结构。在定义模型时，继承
BaseModel 会自动继承其 model_validate 方法，以实现数据的反序列化。

在进行反序列化的过程中，若接口返回参数为基本类型或未实现 model_validate 方法，MicroRequest会尝试直接以 json 格式返回数据。

```python
from pydantic import BaseModel


class Response(BaseModel):
    name: str
    age: int


response = Response.model_validate({'name': 'focus-micro-py', 'age': 1})

print(response)
print(type(response))

# name='focus-micro-py' age=1
# <class '__main__.Response'>
```

## 服务封装

具体的服务封装实现可参考 calc_client.py 文件，在进行封装时，只需要考虑服务名，接口签名等信息即可，不需要客户端考虑接口通讯细节。

```python
from typing import Union

from common.request import MicroRequest
from common.model import MicroJsonResponse, ServiceInfo

request = MicroRequest()


@request.get(server_name="calc_server", path='/add/{a}/{b}')
def add_client(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    pass


@request.post(server_name="REGISTER_CENTER", path='/register')
def register_client(service: ServiceInfo) -> MicroJsonResponse:
    pass
```

在上述实例中，通过实例化 MicroRequest 类，定义了装饰器对象，在进行请求时，根据HTTP请求动作
GET、POST等调用对应装饰器实现。在装饰器中，需要指定服务名和请求路径，装饰器会自动解析服务名，进行服务发现与负载均衡，并根据方法签名向指定服务发起请求。

# 服务注册

服务在启动时，需要向注册中心发起注册请求，以实现服务发现。服务注册不仅应该在启动后进行注册，也需要定期向服务器发起注册保持心跳连接。在
`common.register.py` 文件中，实现了服务注册的相关接口。在实现微服务接口时，只需要引入并注册相关接口即可。

```python
import asyncio

from fastapi import FastAPI

from common.register import register_task

app = FastAPI()


async def startup_event():
    """
    fastapi 启动事件
    注册定时服务
    :return:
    """
    # SERVER_NAME: 服务注册名称
    # SERVER: 服务通讯接口信息
    # KEEPALIVE_TIME: 心跳时间，默认60s
    asyncio.create_task(register_task(SERVER_NAME, SERVER, KEEPALIVE_TIME))


if __name__ == '__main__':
    app.add_event_handler("startup", startup_event)
```
