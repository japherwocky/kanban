import os
import yaml
from pathlib import Path

CONFIG_FILE = Path(os.environ.get("KANBAN_CONFIG_PATH", Path.home() / ".kanban.yaml"))


def ensure_config_dir():
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)


def load_config():
    ensure_config_dir()
    if not CONFIG_FILE.exists():
        return {"server": {"url": "http://localhost:8000"}, "auth": {}}
    with open(CONFIG_FILE) as f:
        return yaml.safe_load(f) or {
            "server": {"url": "http://localhost:8000"},
            "auth": {},
        }


def save_config(config):
    ensure_config_dir()
    with open(CONFIG_FILE, "w") as f:
        yaml.dump(config, f)


def get_server_url():
    config = load_config()
    return config.get("server", {}).get("url", "http://localhost:8000")


def set_server_url(url):
    config = load_config()
    config["server"] = {"url": url}
    save_config(config)


def get_token():
    config = load_config()
    return config.get("auth", {}).get("token")


def set_token(token):
    config = load_config()
    config["auth"] = {"token": token}
    save_config(config)


def clear_token():
    config = load_config()
    config["auth"] = {}
    save_config(config)


def get_api_key():
    """Get the preferred API key from config."""
    config = load_config()
    return config.get("auth", {}).get("api_key")


def set_api_key(api_key):
    """Set the preferred API key in config."""
    config = load_config()
    if "auth" not in config:
        config["auth"] = {}
    config["auth"]["api_key"] = api_key
    save_config(config)


def clear_api_key():
    """Clear the API key from config."""
    config = load_config()
    if "auth" in config:
        config["auth"].pop("api_key", None)
        save_config(config)
