from os import environ as _env

from dotenv import load_dotenv as _load_dotenv

_load_dotenv()


ADMIN_USERNAME: str = "admin"
ADMIN_PASSWORD: str = "password"
LINK_EXPIRY: int = 0
MAX_LINK_EXPIRY: int = 0
SESSION_EXPIRY: int = 86400  # 1 day
ALLOW_REGISTRATION: bool = False


_config_options = [item for item in globals().keys() if not item.startswith("_")]

for option in _config_options:
    o = _env.get(option)
    if o is None:
        raise ValueError(
            f"Missing config option: {option}. Please set it in the .env file."
        )
    if isinstance(globals()[option], str):
        globals()[option] = o
    elif isinstance(globals()[option], bool):
        globals()[option] = o.lower() == "true"
    elif isinstance(globals()[option], int):
        globals()[option] = int(o)
    else:
        raise TypeError(f"Invalid type for config option: {option}")
