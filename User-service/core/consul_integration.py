import consul
from loguru import logger
from config.config import DICT_ENVS

def register_consul() -> None:
    try:
        consul_server = consul.Consul(host=DICT_ENVS["CONSUL_HOST"], port=DICT_ENVS["CONSUL_PORT"],
                                      token=DICT_ENVS["CONSUL_TOKEN"])

        service_id = "user-service"
        service_name = "user-service"
        service_port = DICT_ENVS["FASTAPI_PORT"]
        service_address = DICT_ENVS["FASTAPI_IP"]

        check = consul.Check.http(
            url=f"http://{service_address}:{service_port}/health",
            interval="10s",
            timeout="1s",
        )

        consul_server.agent.service.register(
            service_name,
            service_id,
            address=service_address,
            port=service_port,
            check=check,
        )
    except consul.ConsulException as e:
        logger.error("Failed to register with Consul")
        raise Exception("Failed to register with Consul") from e
