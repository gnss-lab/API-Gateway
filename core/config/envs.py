from http.client import GATEWAY_TIMEOUT
from environs import Env

env = Env()
env.read_env()

DICT_ENVS = {}

DICT_ENVS["GATEWAY_TIMEOUT"] = env.int("GATEWAY_TIMEOUT", 59)
DICT_ENVS["MOSGIM_SERVICE_URL"] = env.str("MOSGIM_SERVICE_URL")


DICT_ENVS["IP_SERVER"] = env.str("IP_SERVER")
DICT_ENVS["PORT_SERVER"] = env.int("PORT_SERVER")
