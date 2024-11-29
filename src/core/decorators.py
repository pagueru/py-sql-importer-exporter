from functools import wraps

from core.logger import logger


def handle_exceptions():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            function_name = func.__name__
            logger.debug(f"Iniciando a função: {function_name}")
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Erro ao processar a função {function_name}: {e}")
                raise

        return wrapper

    return decorator
