import os

from dotenv import load_dotenv


# Parse a `.env` file and load the variables inside into environment variables
load_dotenv()


class ImproperlyConfigured(Exception):
    """Raises when a environment variable is missing."""

    def __init__(self, variable_name, *args, **kwargs):
        self.variable_name = variable_name
        self.message = f'Set the {variable_name} environment variable.'
        super().__init__(self.message, *args, **kwargs)


def get_env_variable(var_name: str) -> str:
    """Get an environment variable or raise an exception.

    Args:
        var_name: a name of a environment variable.

    Returns:
        A value of the environment variable.

    Raises:
        ImproperlyConfigured: if the environment variable is not set.
    """
    try:
        return os.environ[var_name]
    except KeyError:
        raise ImproperlyConfigured(var_name)


BOT_TOKEN: str = get_env_variable('BOT_TOKEN')

DB_HOST: str = get_env_variable('DB_HOST')
DB_PORT: str = get_env_variable('DB_PORT')
DB_NAME: str = get_env_variable('DB_NAME')
DB_USER: str = get_env_variable('DB_USER')
DB_PASSWORD: str = get_env_variable('DB_PASSWORD')
