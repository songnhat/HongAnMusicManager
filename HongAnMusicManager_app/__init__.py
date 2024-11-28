from flask import Flask
from HongAnMusicManager_app.api import rest_api
from .common import database
import logging
from dynaconf import FlaskDynaconf, settings
from random import seed
from urllib.parse import urlparse
import MySQLdb
from MySQLdb._exceptions import OperationalError
from time import sleep

db = database.db

ENVVAR_PREFIX_FOR_DYNACONF = "HONGAN"
ENVVAR_FOR_DYNACONF = "HONGAN_SETTINGS"


def create_app(flask_env=None, db_uri=None):
    app = Flask(__name__)

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.info("Loading configuration")
    FlaskDynaconf(
        app,
        ENVVAR_FOR_DYNACONF=ENVVAR_FOR_DYNACONF,
        ENVVAR_PREFIX_FOR_DYNACONF=ENVVAR_PREFIX_FOR_DYNACONF,
    )
    if app.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)
    if flask_env:
        app.config.setenv(flask_env)
        settings.setenv(flask_env.upper())
    if db_uri:
        app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
        settings.set("SQLALCHEMY_DATABASE_URI", db_uri)
    seed()
    logger.info("Checking database connection")

    if not check_db_connection_available():
        raise Exception("Database connection timeout")

    logger.info("Initializing app")
    db.init_app(app)

    app.register_blueprint(rest_api.api_bp, url_prefix="")

    return app


def check_db_connection_available():
    logger = logging.getLogger(__name__)
    retry_count = 0
    while retry_count < 90:
        try:
            dbc = urlparse(settings.SQLALCHEMY_DATABASE_URI)
            conn = MySQLdb.connect(
                host=dbc.hostname,
                user=dbc.username,
                password=dbc.password,
                database=dbc.path.lstrip("/"),
            )
            conn.ping()
            return True
        except OperationalError:
            retry_count = retry_count + 1
            logger.warning("Wating for db connection is available!")
            sleep(1)
    return False
