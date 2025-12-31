import os
import yaml
from pathlib import Path

CONFIG_DIR = Path(os.environ.get("KANBAN_CONFIG_DIR", Path.home() / ".kanban"))
CONFIG_FILE = CONFIG_DIR / "config.yaml"


def ensure_config_dir():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_config():
    ensure_config_dir()
    if not CONFIG_FILE.exists():
        return {"server": {"url": "http://localhost:8000"}, "auth": {}}
    with open(CONFIG_FILE) as f:
        return yaml.safe_load(f) or {"server": {"url": "http://localhost:8000"}, "auth": {}}


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
