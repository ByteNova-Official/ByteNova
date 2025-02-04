# File: app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import redis, logging, os
from flask_socketio import SocketIO
from flask_cors import CORS

db = SQLAlchemy()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config_name)
    db.init_app(app)
    
    return app

if os.getenv('FLASK_ENV') == 'production':
    app = create_app('config.ProductionConfig')
else:
    app = create_app('config.DevelopmentConfig')

CORS(app, origins='*')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

socketio = SocketIO(app)

# Create a Redis connection
app.r = redis.Redis(host=app.config['REDIS_HOST'], port=6379, db=0)

from app.routes import inference_job_routes  # import the inference job routes
from app.routes import invocation_routes  # import the invocation routes
from app.routes import worker_routes  # import the worker routes
from app.routes import user_routes  # import the user routes
from app.routes import model_routes  # import the model routes
from app.routes import api_key_routes  # import the api key routes
from app.routes import login_routes  # import the login routes
from app.routes.worker_socketio_routes import *  # import the worker socketio routes

app.register_blueprint(inference_job_routes.bp, url_prefix='/inference_jobs')  # register the inference job blueprint
app.register_blueprint(invocation_routes.bp, url_prefix='/invocations')  # register the invocations blueprint
app.register_blueprint(worker_routes.bp, url_prefix='/workers')  # register the workers blueprint
app.register_blueprint(user_routes.bp, url_prefix='/users')  # register the users blueprint
app.register_blueprint(model_routes.bp, url_prefix='/models')  # register the models blueprint
app.register_blueprint(api_key_routes.bp, url_prefix='/api_keys')  # register the api keys blueprint
app.register_blueprint(login_routes.bp, url_prefix='/login')  # register the login blueprint

# Check if the log directory exists
logdir = os.path.join(os.getcwd(), 'logs')
if not os.path.exists(logdir):
    os.makedirs(logdir)

# Make sure app.logger uses the correct logger
def setup_logging():
    if not app.debug:
        # In production mode, add log handler to sys.stderr.
        app.logger.addHandler(logging.StreamHandler())
        app.logger.setLevel(logging.INFO)

handler = logging.FileHandler(os.path.join(logdir, 'flask.log'))
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)
