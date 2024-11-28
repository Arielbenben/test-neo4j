from flask import Flask
from app.routes.phone_route import phone_blueprint


app = Flask(__name__)


app.register_blueprint(phone_blueprint, url_prefix='/api')


if __name__ == '__main__':
    app.run()