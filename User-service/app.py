from config.config import create_app
from core.consul_integration import register_consul

if __name__ == '__main__':
    app = create_app()

    register_consul()

    app.run(debug=True)
