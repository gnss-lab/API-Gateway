from src.config.config import create_app
from src.config.envs import DICT_ENVS
import uvicorn

if __name__ == "__main__":

    app, _, _ = create_app()
    uvicorn.run(app, host=DICT_ENVS["FASTAPI_IP"], port=DICT_ENVS["FASTAPI_PORT"])
