from environs import Env

env = Env()
env.read_env()

DICT_ENVS = {}

DICT_ENVS["GATEWAY_TIMEOUT"] = env.int("GATEWAY_TIMEOUT", 59)

DICT_ENVS["FASTAPI_IP"] = env.str("FASTAPI_IP")
DICT_ENVS["FASTAPI_PORT"] = env.int("FASTAPI_PORT")

DICT_ENVS["LOGSTASH_HOST"] = env.str("LOGSTASH_HOST")
DICT_ENVS["LOGSTASH_PORT"] = env.int("LOGSTASH_PORT")
