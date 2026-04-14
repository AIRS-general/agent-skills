from dependency_injector import containers, providers

from app.core.config import Settings
from app.core.logging import logger as app_logger
from app.db.session import (
    create_engine_from_settings,
    create_session,
    create_session_factory,
)


class Container(containers.DeclarativeContainer):
    logger = providers.Object(app_logger)
    settings = providers.Singleton(Settings)
    engine = providers.Singleton(create_engine_from_settings, settings=settings)
    session_factory = providers.Singleton(create_session_factory, engine=engine)
    session = providers.Factory(create_session, session_factory=session_factory)


container = Container()


def get_logger():
    return container.logger()


def get_settings():
    return container.settings()


def get_db():
    db = container.session()
    try:
        yield db
    finally:
        db.close()
