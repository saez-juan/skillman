"""Configuration management for skillman."""

import sys
from pathlib import Path
from typing import List

import tomli_w

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


# Default configuration directory and file
CONFIG_DIR = Path.home() / ".claude" / "skillman"
CONFIG_FILE = CONFIG_DIR / "config.toml"
DEFAULT_SKILLS_PATH = CONFIG_DIR / "skills"


def get_default_config() -> dict:
    """
    Return the default configuration.

    Returns:
        Dictionary with default configuration values
    """
    return {
        "skills_paths": [str(DEFAULT_SKILLS_PATH)]
    }


def ensure_config_exists() -> Path:
    """
    Ensure the configuration file exists, creating it with defaults if necessary.

    Returns:
        Path to the configuration file
    """
    if not CONFIG_FILE.exists():
        # Create config directory if it doesn't exist
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)

        # Create default skills directory
        DEFAULT_SKILLS_PATH.mkdir(parents=True, exist_ok=True)

        # Write default configuration
        default_config = get_default_config()
        with open(CONFIG_FILE, "wb") as f:
            tomli_w.dump(default_config, f)

    return CONFIG_FILE


def load_config() -> dict:
    """
    Load configuration from the config file.

    If the config file doesn't exist, it will be created with default values.

    Returns:
        Dictionary with configuration values
    """
    config_path = ensure_config_exists()

    with open(config_path, "rb") as f:
        config = tomllib.load(f)

    return config


def get_skills_paths() -> List[Path]:
    """
    Get the list of skills paths from configuration.

    Returns:
        List of Path objects for skills directories
    """
    config = load_config()
    paths_str = config.get("skills_paths", [str(DEFAULT_SKILLS_PATH)])

    # Expand ~ and convert to Path objects
    paths = []
    for p in paths_str:
        expanded = Path(p).expanduser()
        paths.append(expanded)

    return paths


def add_skills_path(path: str) -> None:
    """
    Add a new skills path to the configuration.

    Args:
        path: Path to add to skills_paths
    """
    config = load_config()
    paths = config.get("skills_paths", [])

    # Normalize the path
    normalized = str(Path(path).expanduser())

    if normalized not in paths:
        paths.append(normalized)
        config["skills_paths"] = paths

        with open(CONFIG_FILE, "wb") as f:
            tomli_w.dump(config, f)


def remove_skills_path(path: str) -> bool:
    """
    Remove a skills path from the configuration.

    Args:
        path: Path to remove from skills_paths

    Returns:
        True if the path was removed, False if it wasn't found
    """
    config = load_config()
    paths = config.get("skills_paths", [])

    # Normalize the path
    normalized = str(Path(path).expanduser())

    if normalized in paths:
        paths.remove(normalized)
        config["skills_paths"] = paths

        with open(CONFIG_FILE, "wb") as f:
            tomli_w.dump(config, f)
        return True

    return False
