import socket

import consul
from loguru import logger

from core.config.envs import DICT_ENVS


def register_consul() -> None:
    try:
        consul_server = consul.Consul(host=DICT_ENVS["CONSUL_HOST"], port=DICT_ENVS["CONSUL_PORT"],
                                      token=DICT_ENVS["CONSUL_TOKEN"])
        print(consul_server)

        service_id = "api-gateway"
        service_name = "api-gateway"
        service_port = DICT_ENVS["FASTAPI_PORT"]
        service_address = DICT_ENVS["FASTAPI_IP"]

        consul_server.agent.service.register(
            service_name,
            service_id,
            address=service_address,
            port=service_port,
        )
    except consul.ConsulException as e:
        logger.error("Failed to register with Consul")
        raise Exception("Failed to register with Consul") from e