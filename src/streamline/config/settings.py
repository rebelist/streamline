from typing import Any

from dynaconf import Dynaconf

settings: Any = Dynaconf(
    envvar_prefix='STREAMLINE',
    settings_files=['settings.toml'],
    dotenv_path='.env',
    environments=False,
    load_dotenv=True,
    frozen=True,
)
