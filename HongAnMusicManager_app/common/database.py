from functools import lru_cache
import logging
from contextlib import contextmanager

from dynaconf import settings
import os
from flask import has_app_context
from flask_sqlalchemy import SQLAlchemy as _BaseSQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy import exc as sql_exc
from sqlalchemy.orm import scoped_session, sessionmaker


class SQLAlchemy(_BaseSQLAlchemy):
    def apply_pool_defaults(self, app, options):
        options = super(SQLAlchemy, self).apply_pool_defaults(app, options)
        options["pool_pre_ping"] = True
        options["pool_recycle"] = 7200
        return options


def get_session():
    global _Session
    if has_app_context():
        _Session = db.session
    if not _Session:
        _create_session_maker()
    return _Session()


def get_engine():
    global _engine
    if not _engine:
        _create_engine()
    return _engine


def pre_ping(session, sample_object=None, remaining_retry=3):
    logger = logging.getLogger(__name__)
    logger.debug("Pre-ping database")
    try:
        if sample_object:
            session.query(sample_object).limit(1).all()
        else:
            session.execute("SELECT 1")
        return True
    except (sql_exc.OperationalError, sql_exc.StatementError) as e:
        logger.debug("Retry connection", exc_info=True)
        session.rollback()
        err_message = str(e)
        if "Can't connect to MySQL server" in err_message:
            logger.error("Cannot connect to database server")
        elif "Can't reconnect until invalid transaction is rolled back" in err_message:
            logger.exception("err")
            logger.info("Trying rollback current session")
        if remaining_retry > 0:
            return pre_ping(session, sample_object, remaining_retry - 1)
    except Exception as e:
        session.rollback()
        raise e


def _create_session_maker():
    global _Session
    global _engine
    _Session = sessionmaker()
    if not _engine:
        _create_engine()
    _Session.configure(bind=_engine)
    _Session = scoped_session(_Session)
    return _Session


def _create_engine():
    global _engine
    database_uri = settings.SQLALCHEMY_DATABASE_URI
    _engine = create_engine(database_uri, pool_pre_ping=True, pool_recycle=7200)


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        if not _is_in_testing_env():
            session.close()


def is_mysql_session(session):
    return session.bind.dialect.name == "mysql"


@lru_cache(maxsize=1)
def _is_in_testing_env():
    current_env = os.getenv("ENV_FOR_DYNACONF")
    if not current_env:
        return False
    return current_env.upper() in ["TESTING", "CACHING", "CI"]


db = SQLAlchemy()
_engine = None
_Session = None
